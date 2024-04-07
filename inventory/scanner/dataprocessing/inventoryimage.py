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

from inventory.scanner.dataprocessing.utils import validate_path
from stitching import Stitcher
from typing import Union
from PIL import Image
import numpy as np
import os


class InventoryImage:
    """
    Class representation of an image which provides the numpy array 
    image definition and the properties of the image such as the width and
    the height.
    This class is intended to store the images of one package detected. Ideally,
    each package should have a visible barcode or QR code attached. Otherwise,
    text will be parsed.

    Parameters
    ----------
        image: Union[str, np.ndarray]
            This is the path to the image file or a numpy array image.

    Raises
    ------
        FileNotFoundError
            This error is raised if the image file is not found.

        TypeError:
            This error is raised if the image shape does not conform to any of the
            established lengths: 4,3, or 2.
    """
    def __init__(self, image: Union[str, np.ndarray]) -> None:
        if isinstance(image, str):
            image = validate_path(image)
            self._img = np.ascontiguousarray(Image.open(image).convert('RGB'))
            self._path = image
        else:
            self._img: np.ndarray = image
            self._path = None
        
        # Image properties
        self._height = None
        self._width = None
        self._channel = None
        self._alpha = None

        # RGBA image
        if len(self._img.shape) == 4:
            self._height, self._width, self._channel, self._alpha = self._img.shape
        # RGB image
        elif len(self._img.shape) == 3:
            self._height, self._width, self._channel = self._img.shape
        # Gray image
        elif len(self._img.shape) == 2:
            self._height, self._width = self._img.shape
        else:
            raise TypeError(f"Unknown image shape {self._img.shape}")

    @property
    def path(self) -> str:
        """
        Attribute to access the path to the image.
        Can be set to :py:class:`str`

        Returns
        -------
            :py:class:`str`: The path to the image.
        """
        return self._path
    
    @path.setter
    def path(self, image_path: str):
        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"The path to the image {image_path} does not exist.")
        self._path = image_path

    @property
    def image(self) -> np.ndarray:
        """
        Attribute to access the image numpy array.
        Can be set to :py:class:`ndarray`

        Returns
        -------
            :py:class:`ndarray`: The image array
        """
        return self._img
    
    @image.setter
    def image(self, img: np.ndarray):
        self._img = img
    
    @property
    def height(self) -> int:
        """
        Attribute to access the image height.
        Can be set to :py:class:`int`

        Returns
        -------
            :py:class:`int`: The image height
        """
        return self._height
    
    @property
    def width(self) -> int:
        """
        Attribute to access the image width.
        Can be set to :py:class:`int`

        Returns
        -------
            :py:class:`int`: The image width
        """
        return self._width
    
    @property
    def channels(self) -> int:
        """
        Attribute to access the image number of channels.
        Can be set to :py:class:`int`

        Returns
        -------
            :py:class:`int`: The image number of channels
        """
        return self._channel
    
    @property
    def alpha(self) -> float:
        """
        Attribute to access the image alpha value.
        Can be set to :py:class:`float`

        Returns
        -------
            :py:class:`float`: The image alpha value
        """
        return self._alpha

    def __repr__(self) -> str:
        template = "Image(image_path={image_path})"
        return template.format(image_path=self._path)


class ShelfImage:
    """
    This class represents image cropped to contain a single shelf on a warehouse.
    This image will show the individual items on the shelf for visual 
    inspection.

    Parameters
    ----------
        detector: str
            Set the detector type for the image stitcher.

        confidence_threshold: float
            Set the confidence threshold when stitching images.
    """
    def __init__(
            self,
            detector: str = "sift",
            confidence_threshold: float = 0.2
        ) -> None:

        self._shelf_segments = list()
        self.stitcher = Stitcher(
            detector=detector, confidence_threshold=confidence_threshold)

    @property
    def shelf_segments(self) -> list:
        """
        Access the shelf_segments property.

        Returns
        -------
            shelf_segments: list
                This contains the list of numpy arrays of images that are 
                part of the shelving. This list of images is to be stitched
                into a single image.
        """
        return self._shelf_segments
    
    @shelf_segments.setter
    def shelf_segments(self, segments: list):
        """
        Set a new value to the shelf_segments parameter.

        Parameters
        ----------
            segments: list
                This new value to set for the shelf_segments.
        """
        self._shelf_segments = segments

    def stitch_images(self):
        """
        This method stitches the shelf segments images that are collected.
        If there are no images collected, it will return None. First collect
        the stitched images ShelfImage.shelf_segments.append(image: np.ndarray).

        Returns
        -------
            image: np.ndarray
                A stitched image.

            None: if no shelf segments were collected in the object.
        """
        if len(self.shelf_segments) > 0:
            panorama = self.stitcher.stitch(self.shelf_segments)
            return panorama
        return None
    
if __name__ == '__main__':
    home_directory = os.path.join( os.path.dirname( __file__ ), '..' )
    image = InventoryImage(os.path.join(home_directory, 'test/samples/barcode_001.jpg'))
    
    print(f"image height = {image.height}")
    print(f"image width = {image.width}")
    print(f"image channels = {image.channels}")
    print(f"image alpha values = {image.alpha}")
    print(f"image type = {type(image.image)}")