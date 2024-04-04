# Copyright 2024 by AisleSolutions. All Rights Reserved. 
# 
# Source code is explicitly for meeting requirements requested by University
# of Calgary Entrepreneurial Capstone Design Project 2024. 
#
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying source code is explicitly forbidden. 

"""
This module will contain helper functions for processing images.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Union
import numpy as np
import os

font = ImageFont.load_default()

def validate_path(source: str) -> str:
    """
    This function checks if the path exists.

    Parameters
    ----------
        source: str
            This is the path to check
    
    Returns
    -------
        source: str
            The path is returned if it exists.

    Raises
    ------
        FileNotFoundError
            This error raised if the path does not exist.
    """
    if not os.path.exists(source):
        raise FileNotFoundError(
            f"The path {source} does not exist.")
    return source

def resize(
    image: np.ndarray, 
    size: tuple=None, 
    min_side: int=None, 
    max_side: int=None
) -> np.ndarray:
    """
    Resizes a numpy image array with the specified size.

    Parameters
    ----------
        image: np.ndarray
            This is the image to resize.

        size: tuple
            (width, height) to resize the image.

        min_side: int
            The image's min side will be equal to min_side after resizing.

        max_side: int
            If after resizing the image's max side is above max_side, 
            resize until the max side is equal to max_side.

    Returns
    -------
        image: np.ndarray
            This is the resized image.
    """    
    scale = None
    shape = image.shape

    # Keep the original shape.
    if size is None:
        size = (shape[1], shape[0])
    image = Image.fromarray((image * 1).astype(np.uint8)).convert("RGB")

    if None not in [min_side, max_side]: 
        scale = compute_resize_scale(shape, min_side=min_side, max_side=max_side)
        size = (int(size[0]*scale), int(size[1]*scale))
            
    image = image.resize(size)
    return np.asarray(image), scale

def rgb2bgr(image:np.ndarray) -> np.ndarray:
    """
    This converts an RGB image to a BGR.

    Parameters
    ----------
        image: np.ndarray
            The RGB image to convert to BGR.

    Returns
    -------
        image: np.ndarray
            This is the BGR image. 
    """
    return image[:, :, ::-1]
    
def normalize(image:np.ndarray, normalization: str, input_type: str="float32") -> np.ndarray:
    """
    Perform image normalization primarily used for model input preprocessing. 
    Translation of values in between 0 and 1.

    Parameters
    ----------
        image: np.ndarray
            This is the image to normalize.

        normalization: str
            This is the type of image normalization to perform.

        input_type: str
            This is the input type of the model. By default it is a float32 model.

    Returns
    -------
        image: np.ndarray
            This is the normalized image.
    """
    if normalization.lower() == "signed":
        return np.expand_dims((image/127.5)-1.0, 0).astype(np.dtype(input_type))
    elif normalization.lower() == "unsigned":
        return np.expand_dims(image/255.0, 0).astype(np.dtype(input_type))
    else:
        return np.expand_dims(image, 0).astype(np.dtype(input_type))
    
def preprocess_image(image: np.ndarray, mode: str='caffe') -> np.ndarray:
    """ 
    Preprocess an image by subtracting the ImageNet mean.
    Method is taken from:: \
    https://github.com/fizyr/keras-retinanet/blob/main/keras_retinanet/utils/image.py#L36

    Parameters
    ----------
        image: np.ndarray of shape (None, None, 3) or (3, None, None).
            The image to preprocess.

        mode: One of "caffe" or "tf".
            - caffe: will zero-center each color channel with
                respect to the ImageNet dataset, without scaling.
            - tf: will scale pixels between -1 and 1, sample-wise.

    Returns
    -------
        The input image with the ImageNet mean subtracted.
    """
    # Mostly identical to "https://github.com/keras-team/keras-applications/blob/master/keras_applications/imagenet_utils.py"
    # except for converting RGB -> BGR since we assume BGR already.

    # Convert always to float32 to keep compatibility with OpenCV.
    image = image.astype(np.float32)

    if mode.lower() == 'tf':
        image /= 127.5
        image -= 1.
        return image
    
    if mode.lower() == 'caffe':
        image -= [103.939, 116.779, 123.68]
        return image
    return image

def compute_resize_scale(image_shape: tuple, min_side: int=800, max_side: int=1333) -> float:
    """ 
    Compute an image scale such that the image size is 
    constrained to min_side and max_side.
    Method is taken from:: \
    https://github.com/fizyr/keras-retinanet/blob/main/keras_retinanet/utils/image.py#L36

    Parameters
    ----------
        image_shape: tuple
            (height, width, channels) image.

        min_side: int
            The image's min side will be equal to min_side after resizing.

        max_side: int
            If after resizing the image's max side is above max_side, 
            resize until the max side is equal to max_side.

    Returns
    -------
        scale: float
            A resizing scale.
    """
    (rows, cols, _) = image_shape
    smallest_side = min(rows, cols)
    # Rescale the image so the smallest side is min_side.
    scale = min_side / smallest_side
    # Check if the largest side is now greater than max_side, which can happen
    # when images have a large aspect ratio.
    largest_side = max(rows, cols)
    if largest_side * scale > max_side:
        scale = max_side / largest_side
    return scale

def sharpen_image(image: np.ndarray, sharpen_iterations: int=1) -> np.ndarray:
    """
    This function sharpens the image based on number of iterations.

    Parameters
    ----------
        image: np.ndarray
            This is the image to sharpen.

        sharpen_iterations: int
            The number of times to sharpen the image.

    Returns
    -------
        image: np.ndarray
            The sharpened image.
    """
    image = Image.fromarray(image)
    for _ in range(sharpen_iterations):
        image = image.filter(ImageFilter.SHARPEN)
    return np.asarray(image)

def clamp_dimension(
        dimension: Union[float, int], 
        max: Union[float, int]=1, 
        min: Union[float, int]=0
    ) -> Union[float, int]:
    """
    Clamps a given dimension in between the minimum and the maximum values
    passed. If the dimension is larger than the maximum, the maximum is returned.
    If the dimension is smaller than the minimum, the minimum is returned.

    Parameters
    ----------
        dimension: float or int
            The dimension to clamp.

        max: The maximum value allowable.

        min: The minimum value allowable.

    Returns
    -------
        dimension: float or int
            The clamped dimension in between the minimum and the maximum.
    """
    return max if dimension > max else min if dimension < min else dimension #NOSONAR

def draw_bounding_box(
        image_draw: ImageDraw.ImageDraw, 
        box: tuple,
        color="LimeGreen",
        width=3
    ):
    """
    Draw bounding boxes on the image.

    Parameters
    ----------
        image_draw: ImageDraw.ImageDraw
            This is the ImageDraw object initialized using Pillow by
            passing an PIL.Image.Image object.

        box: tuple
            This contains ((xmin, ymin), (xmax, ymax)) bounding box coordinates
            in pixels.

        color: str
            The color of the bounding box.

        width: int
            This is the width of the lines of the bounding box.
    """
    if (box[0][0] < box[1][0]) and (box[0][1] < box[1][1]):
        image_draw.rectangle(
            box,
            outline=color,
            width=width)
    
def draw_text(
        image_draw: ImageDraw.ImageDraw,
        text: str,
        position: tuple,
        color: str="black", 
        align: str="left"
    ):
    """
    Draws text on the image.

    Parameters
    ----------
        image_draw: ImageDraw.ImageDraw
            This is the ImageDraw object initialized using Pillow by
            passing an PIL.Image.Image object.

        text: str
            This is the text to draw on the image.

        position: tuple
            This is the (xmin, ymin) position to place the text on the image.

        color: str
            This is the color of the text.

        align: str
            This is the text alignment on the image.
    """
    image_draw.text(
        position,
        text,
        font=font,
        align=align,
        fill=color
    )