import numpy as np
from skimage.color import grey2rgb, rgb2grey


def convert_channels(image, channel):
    '''
       Convert 2 dimensional image to 3 dimension. 
       Convert black and white image to colour and viceversa
       Channel is the value inferred by compute_image_shape method
    '''
    if image.ndim == 2:
        dim = 1
        old_channel = 1
    elif image.ndim == 3:
        old_channel = image.shape[-1]
        dim = 3

    if old_channel == 1:
        if channel == 3:
            if dim == 3:
                image = np.squeeze(image, axis=2)
            image = grey2rgb(image)
        elif image.ndim == 2:
            image = image.reshape(image.shape[0], image.shape[1], 1)
    elif old_channel == 3 and channel == 1:
        image = rgb2grey(image).reshape(image.shape[0], image.shape[1], 1)
    return image

