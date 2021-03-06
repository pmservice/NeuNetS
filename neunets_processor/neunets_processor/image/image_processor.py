import numpy as np
from PIL import Image
import json 
from neunets_processor.image.image_utils import convert_channels
from keras.models import Model, load_model

from typing import List, Dict

class ImageProcessor:

    def __init__(self,
                 model_path: str,
                 metadata_path: str,
                 loaded_model: Model = None) -> None:
        '''
          Parameters:
         ______________
          model_path : path to the keras model object generated by neunets
          metadata_path : path to the metadata.json object generated by neunets
          loaded_model : if a model is already loaded in memory, then this can be passed.
                         The pacakge will not load it again. 
          Returns:
         __________
           None

          Initialize imagepreprocessor. Imagepreprocessor transforms image to a format that can be input to keras model,
          predicts on the model and returns probabilities corresponding to each label
        '''

        if loaded_model:
            self.keras_model = loaded_model
        else:
            self.keras_model = load_model(model_path)
        self.image_shape = self._compute_image_shape() #image_height, image_width, num_channel
        metadata = self._load_metadata(metadata_path)
        self.mean_values = metadata[1]['mean']
        self.std_values = metadata[1]['std']
        self.label_mapping = metadata[0]

    def preprocess(self, image: List[np.ndarray]) -> np.ndarray:
        '''
          Parameters:
         ______________
          image: List comprised of only one input_image as numpy array

          Returns: 
         __________
          a resized, normalized image as a numpy array

          Convert input image to the dimensions compatible with keras model. This method is used
          if one were manually inferring a loaded model outside of WML. If one wants to predict it
          directly, without having to preprocess or postprocess, invoke predict method

        '''
        image = image[0]
        image_height, image_width, num_channels = self.image_shape
        image = np.array(image)
        image = Image.fromarray(image.astype('uint8'))
        image = image.resize((image_height, image_width), Image.ANTIALIAS)
        image = np.asarray(image, dtype=np.uint8)
        image = convert_channels(image, num_channels)
        image = np.resize(image, (1,image_height, image_width, num_channels))
        image = self._normalize_image(image)
        return image

    def predict(self, image: List[np.ndarray]) -> Dict:
        '''
          Parameters:
         ______________
          image: List comprised of only one input_image as numpy array
          Returns:
         __________
          a dict with key label name and value prediction probability of that label
          a prediction for an image may be {"cat": 0.8, "dog": 0.2}

          preprocess image, inference on keras model and postprocess the prediction
        '''
        preprocessed_image = self.preprocess(image)
        result = self.keras_model.predict(preprocessed_image)
        label_prob = self.postprocess(result[0])
        return label_prob

    def postprocess(self,result: np.ndarray) -> Dict:
        '''
          Parameters:
         ______________
          result : prediction probabilities output by keras model 

          Returns:
         __________
          a dict with key label name and value prediction probability of that label

          convert probabilities array to {label1: prob1, label2:prob2}
        '''
        probabilities = {}
        for index in range(len(result)):
            probabilities[self.label_mapping[str(index)]] =  result[index]
        return probabilities

    def _compute_image_shape(self):
        '''
            Infer image dimensions based on the first layer of the model
            returns image_height, image_width, num_channel
        '''
        input_layer = self.keras_model.layers[0]
        input_shape = input_layer.input_shape
        return (input_shape[1], input_shape[2], input_shape[3])

    def _normalize_image(self, image: List) -> np.array:
        '''
          Parameters:
         ______________
          image : the representation of image

          Returns:
         __________
          normalized image returned as a numpy array

          normalize image using mean and std values derived from training data
        '''
        image = np.asarray(image, dtype=np.float64)
        image /= 255.0
        image -= self.mean_values
        image /= self.std_values
        return image

    def _load_metadata(self, metadata_path) -> tuple:
        '''
          Parameters:
         ______________
          metadata_path : path of metadata.json that is generated by neunets

          Returns:
         __________
          label_mapping dict and mean and std tuple

          loads metadata file
        '''

        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return (metadata['label_mapping'], metadata['data_stats']) #labels, metadata
