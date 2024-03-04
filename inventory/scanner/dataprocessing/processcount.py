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

from inventory.scanner.dataprocessing.utils import (
    draw_bounding_box,
    draw_text
)
from PIL import Image, ImageDraw
import numpy as np


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
            parameters: Parameters,
            show: bool=False
        ) -> None:
        
        from inventory.scanner.runners import (
            IdentificationDetector, 
            PackageDetector, 
            TextDetector
        )
        self.package_detector = PackageDetector(
            model=path_package_model,
            parameters=parameters
        )
        self.identification_detector = IdentificationDetector(
            model=path_identification_model,
            parameters=parameters
        )
        self.text_detector = TextDetector()
        self.show = show

    def process_packages(self, image: np.ndarray):
        """
        Thread 1: Detect Packages -> Crop Image -> Search for text in the detections.

        Parameters
        ----------
            image: np.ndarray
                This is the image to detect packages and texts. 

        Returns
        -------

        """
        boxes, scores, labels = self.package_detector.detect(image)
        if self.show:
            image_drawn = Image.fromarray(image)
            image_draw = ImageDraw.Draw(image_drawn)
        
        for box, score, label in zip(boxes, scores, labels):
            box = box.astype(int)
            if self.show:
                draw_bounding_box(
                    image_draw, ((box[0], box[1]), (box[2], box[3])))
                
            # Decode the barcodes and QR codes by passing a cropped image to 
            # the zxing-cpp dependency.
            image_copy = image.copy()
            image_cropped = image_copy[box[1]:box[3], box[0]:box[2], :]
            _, _, texts = self.text_detector.detect(image_cropped)

            if self.show:
                text = f"{label} {round(score*100, 2)} ".join(texts)
                draw_text(image_draw, text, (box[0], box[1]-10), color="white")

        if self.show:
            image = np.asarray(image_drawn)

        return image, True

    def process_codes(self, image: np.ndarray):
        """
        Thread 2: Detect Barcodes and QR Codes -> Crop image -> Decode detections.

        Parameters
        ----------
            image: np.ndarray
                This is the image to detect barcodes and QR codes. This image
                should be the cropped package image.

        Returns
        -------

        """
        boxes, scores, labels = self.identification_detector.detect(image)
        if self.show:
            image_drawn = Image.fromarray(image)
            image_draw = ImageDraw.Draw(image_drawn)

        for box, score, label in zip(boxes, scores, labels):
            if self.show:
                draw_bounding_box(
                    image_draw, ((box[0], box[1]), (box[2], box[3])))

            # Decode the barcodes and QR codes by passing a cropped image to 
            # the zxing-cpp dependency.
            image_copy = image.copy()
            image_cropped = image_copy[box[1]:box[3], box[0]:box[2], :]
            decodes = self.identification_detector.decode(image_cropped)

            # Assuming only one barcode/QR code was decoded because it is
            # passing an image containing only one code.
            decode = None
            if len(decodes) > 0:
                decode = decodes[0]

            if self.show:
                if label == 0:
                    text = f"Barcode {round(score*100, 2)}"
                elif label == 1:
                    text = f"QR Code {round(score*100, 2)}"
                else:
                    text = f"{label} {round(score*100, 2)}"

                if decode is not None:
                    text += f"{decode.text}, {decode.format}, {decode.content_type}"

                draw_text(image_draw, text, (box[0], box[1]-10), color="white")
        
        if self.show:
            image = np.asarray(image_drawn)

        # TODO: Return CodeImage objects
        return image, True


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

