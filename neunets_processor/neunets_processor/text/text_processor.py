import json
import numpy as np

from keras.models import Model, load_model
from neunets_processor.text import text_utils

from typing import List, Dict

class TextProcessor:

    def __init__(self,
                 model_path: str,
                 metadata_path: str,
                 word_mapping_file: str,
                 loaded_model : Model = None) -> None:
        '''
          Parameters:
         ______________
          model_path : path to the keras model object generated by neunets
          metadata_path : path to the metadata.json object generated by neunets
          word_mapping_file : path to word_mapping.json object generated by neunets
          loaded_model : if a model is already loaded in memory, then this can be passed.
                         The pacakge will not load it again. 
          Returns:
         __________
           None

          Initialize textpreprocessor. Textpreprocessor transforms text to a format that can be input to keras model,
          predicts on the model and returns probabilities corresponding to each label
        '''

        if loaded_model:
            self.keras_model = loaded_model
        else:
            self.keras_model = load_model(model_path)
        self.max_sentence_length = self._extract_max_sentence_length()
        self.word_mappings = self._load_word_mappings(word_mapping_file)
        self.label_mapping = self._load_label_mapping(metadata_path)


    def preprocess(self, text: List[str]) -> List[int]:
        '''
          Parameters:
         ______________
          text : The text to be preprocessed
          Returns:
         __________
          a list of integers.

          tokenizes text, converts tokens to numbers and pad the tokens to match max_sentence_length
          This method is used if one were manually inferring a loaded model outside of WML. If one wants to predict it
          directly, without having to preprocess or postprocess, invoke predict method
        '''
        text = text[0]
        tokenized_text = text_utils.tokenize(text)
        preprocessed_text = text_utils.pad_and_str2idx(self.word_mappings, 
                                            self.max_sentence_length,
                                             tokenized_text.split(" "))
        text_length = len(preprocessed_text)
        preprocessed_text = np.resize(np.asarray(preprocessed_text), (1,text_length))
        return preprocessed_text

    def predict(self, text: List[str]) -> Dict:
        '''
          Parameters:
         ______________
          text : list of test data
          Returns:
         __________
          a dict with key label name and value prediction probability of that label
          a prediction for a review might be {"good": 0.8, "bad": 0.2}

          preprocess text, inference on keras model and postprocess the prediction
        '''
        preprocessed_text = self.preprocess(text)
        result = self.keras_model.predict(preprocessed_text)
        label_prob = self.postprocess(result[0])
        return label_prob

    def postprocess(self, result: np.ndarray) -> Dict:
        '''
          Parameters:
         ______________
          result : prediction probabilities output by keras model 

          Returns:
         __________
          a dict with key label name and value prediction probability of that label
          a prediction for a review might be {"good": 0.8, "bad": 0.2}

          convert prediction probabilities array to {label1: prob1, label2:prob2}
        '''
        probabilities = {}
        for index in range(len(result)):
            probabilities[self.label_mapping[str(index)]] =  result[index]
        return probabilities

    def _extract_max_sentence_length(self) -> int:
        '''
          infer shape of input sentence_length from the first layer of keras model
        '''
        input_layer = self.keras_model.layers[0]
        max_sentence_length = input_layer.input_shape[1]
        return max_sentence_length

    def _load_word_mappings(self, word_mapping_file: str) -> Dict:
        '''
          Parameters:
         ______________
          word_mapping_file : name of the word mapping file 

          Returns:
         __________
          a dict whose keys are the most common words and values are their corresponding integer mapping

          load word_mapping file
        '''
        with open(word_mapping_file, "r") as f:
            word_mapping = json.load(f)
        return word_mapping

    def _load_label_mapping(self, metadata_path : str) -> Dict:
        '''
          Parameters:
         ______________
          metadata_path : path of metadata.json that is generated by neunets

          Returns:
         __________
          label_mapping dict: 

          load metadata file
        '''
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return metadata['label_mapping'] #labels
