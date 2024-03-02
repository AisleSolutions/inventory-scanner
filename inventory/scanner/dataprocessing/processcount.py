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
This library contains functions that are responsible for detecting objects
of interest given an image.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from inventory.scanner.runners import Parameters

from inventory.scanner.runners import IdentificationModel, PackageModel
from inventory.scanner.dataprocessing.utils import clamp_dimension
#from autocorrect import Speller
import numpy as np
# import enchant
# import easyocr
# import cv2
# import re

"""This needs to run only once to load the model into memory."""
# # This object detects texts in images.
# reader = easyocr.Reader(['ch_sim','en']) 
# # This object corrects the spelling in texts.
# speller = Speller(lang='en')
# # This object contains words in the English dictionary for correct spelling.
# dictionary = enchant.Dict("en_US")

# import tensorflow as tf


class ProcessCount:
    """
    This class performs multithreading to provide separate threads for 
    detecting packages, barcodes/QRcodes, etc.

    The detections are then processed to infer on the package counts and
    the barcodes/QRCodes they belong to for classification. 

    Single threads should be provided for the following:
    1) Package detections -> Each detection is cropped and any text is searched.
    2) Barcode/QR code detections.
    
    Then once the threads are merged, the packages and detected barcodes/QR codes
    are paired. Only one barcode/QR code should be paired per detection.

    The package detections that did not have a barcode/QR code or texts 
    will not be considered as valid packages. The result should yeild the 
    following tuple:: \
        (
            cropped package image: InventoryImage, 
            text: str,
            barcode/QR code: InventoryImage
        )

    Parameters
    -----------
        path_package_model: str
            This is the path to the package detection model.

        path_identification model: str
            This is the path to the model that detects barcodes and QR codes.

        parameters: Parameters
            This contains the model parameters to control the model's
            behaviour.
    """
    def __init__(
            self,
            path_package_model: str,
            path_identification_model: str,
            parameters: Parameters
        ) -> None:
        
        self.package_model = PackageModel(
            model=path_package_model,
            parameters=parameters
        )
        self.identification_model = IdentificationModel(
            model=path_identification_model,
            parameters=parameters
        )

    def process(self, image: np.ndarray):
        """
        Multithreading occurs here to process the detections 
        (packages and their respective barcodes and QR codes).


        """
        boxes, scores, labels = self.package_model.detect(image)

        print(f"{labels=}")

        # TODO: Return the frame with bounding boxes. Also draw if --show is enabled.
        return image, True


def barcode_detector(image: Image) -> bool:
    """
    This function detects and decodes barcodes.

    Parameters
    ----------
        image: Image
            This is the class representation of the image to provide aspects
            for storing barcode locations, barcode images, decoded barcodes, etc.

    Returns
    -------
        True: If the image object contains barcodes.
        False: If the image object does not contain barcodes.
    """
    
    bd = cv2.barcode.BarcodeDetector()
    _, decoded_info, _, detections = bd.detectAndDecodeWithType(image.image)

    if detections is None:
        image.hasBarcode = False
        return False
        
    image.hasBarcode = True
    if len(decoded_info):
        image.add_barcode_decoded_info(decoded_info)
    for detection in detections:
        bounding_box = cv2.boundingRect(detection)
        x,y,w,h = bounding_box
        x = clamp_dimension(x, max=image.width, min=0)
        y = clamp_dimension(y, max=image.height, min=0)
        image.add_barcode_bounding_box([x,y,w,h])

        # crop the image only around the detected barcode.
        barcode_img = image.image[y:y+h, x:x+w].copy()
        image.add_barcode_image(barcode_img)
    return True

def qrcode_detector(image: Image) -> bool:
    """
    This function detects and decodes QR codes.

    Parameters
    ----------
        image: Image
            This is the class representation of the image to provide aspects
            for storing  QR code locations, QR code images, decoded QR codes, etc.

    Returns
    -------
        True: If the image object contains QR codes.
        False: If the image object does not contain QR codes.
    """
    qcd = cv2.QRCodeDetector()
    _, decoded_info, poly_points, _ = qcd.detectAndDecodeMulti(image.image)

    if poly_points is None:
        image.hasQRCode = False
        return False
    
    image.hasQRCode = True
    if len(decoded_info):
        image.add_qrcode_decoded_info(decoded_info)
    for points in poly_points:
        bounding_box = cv2.boundingRect(points)
        x,y,w,h = bounding_box
        x = clamp_dimension(x, max=image.width, min=0)
        y = clamp_dimension(y, max=image.height, min=0)
        image.add_qrcode_bounding_box([x,y,w,h])

        # crop the image only around the detected barcode.
        qrcode_img = image.image[y:y+h, x:x+w].copy()
        image.add_qrcode_image(qrcode_img)
    return True

def text_detector(image: Image) -> bool:
    """
    This function detects and decodes text.

    Parameters
    ----------
        image: Image
            This is the class representation of the image to provide aspects
            for storing text locations, text images, decoded texts, etc.

    Returns
    -------
        True: If the image object contains text.
        False: If the image object does not contain text.
    """

    # Use EasyOCR
    # For each text process to remove special characters, lower case, and spell check
    # Use pyenchant to check if the words are existing

    detections = reader.readtext(image.image)
    if detections is None:
        image.hasText = False
        return False

    image.hasText = True
    for detection in detections:
        # The 3rd element is the score of the text.
        location, text, _ = detection
        # remove special characters and convert to lower characters
        text = re.sub('\W+','', text).lower()
        # autocorrect spelling
        text = speller(text)
        # check if the text is a valid word
        if dictionary.check(text):
            image.hasText = True
            image.add_text(text)

            location = [
                location[0][0], 
                location[0][1], 
                location[2][0]-location[0][0], 
                location[2][1]-location[0][1]
            ]
            # text bounding box
            image.add_text_bounding_box(location)

            x,y,w,h = location
            # crop the image only around the detected barcode.
            text_img = image.image[y:y+h, x:x+w].copy()
            image.add_text_image(text_img)
    return True

def shelf_detector(image: Image) -> bool:
    """
    This function detects if the image contains shelving. Features of the shelf
    should include items if present and uniform horizontal lines. 

    Parameters
    ----------
        image: Image
            This is the class representation of the image to provide aspects
            for storing shelving locations in the image, shelving image
            arrays.

    Returns
    -------
        True if the image contains shelving.
        False if the image does not contain shelving.
    """
    # TODO: Implement this function.
    # Perhaps look into the Hough Transforms for detecting lines in the image
    # and decoding lines to be a pattern for shelving. 
    # https://www.geeksforgeeks.org/line-detection-python-opencv-houghline-method/
    # TODO: This needs to be a model.

def vacant_slots_detector(image: Image) -> bool:
    """
    This function detects if the image that has shelving contains vacant 
    slots in the shelving or empty rows. See the link provided below for 
    more information. This is useful for a quick check of zero items available.

    Parameters
    ----------
        image: Image
            This is the class representation of the image to provide aspects
            for storing empty locations in the image.

    Returns
    -------
        True if shelving has empty item slots.
        False if the shelving is full/contains items.
    """
    # TODO: Implement this function.
    # https://medium.com/analytics-vidhya/identifying-empty-shelf-spaces-using-template-matching-in-opencv-6be8d4caa80e

def items_detector(image: Image) -> int:
    """
    This function should detect the number of items in a given image. This is
    for sanity checking that the number of items counted from the 2D Lidar
    matches with the number of items counted in this function. 

    Parameters
    ----------
        image: Image
            This is the class representation of the image to provide aspects
            for the number of items counted in this function. Also this object
            contains the numpy image array to process for image counting.

    Returns
    --------
        0 if there are no items counted
        An integer representing the number of items counted in the image.
    """
    # TODO: Implement this function.
    # Try these solutions:
    # 1) https://www.askpython.com/python/examples/count-objects-in-an-image
    # 2) https://www.geeksforgeeks.org/count-number-of-object-using-python-opencv/