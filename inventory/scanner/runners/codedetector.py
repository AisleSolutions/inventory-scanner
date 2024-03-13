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

from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List
if TYPE_CHECKING:
    from inventory.scanner.runners import Parameters

from inventory.scanner.kerasretinanet.models.tflite import TFliteRunner
from inventory.scanner.dataprocessing.utils import sharpen_image
import numpy as np
import zxingcpp


class IdentificationDetector:
    """
    This class provides methods for detecting barcodes and QR codes using
    a YoloV5 Tflite detection model and then decoding the detections into their 
    or number text representations.

    Parameters
    ----------
        model: str
            This is the path to the barcode-qrcode detection model. Current
            supported model are TFLite models.

        parameters: Parameters
            This contains model parameters.
    """
    def __init__(
            self,
            model: str,
            parameters: Parameters
        ) -> None:
        
        self.loaded_model = TFliteRunner(
            model=model,
            parameters=parameters
        )
        self.parameters = parameters

    def detect(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        This method performs Barcode and QRCode detections given a numpy image.

        Parameters
        ----------
            image: np.ndarray
                This is a numpy array image.

        Returns
        -------
            boxes: np.ndarray
                These are the non-normalized bounding boxes of the 
                detections in the format [[xmin, ymin, xmax, ymax], [...], ...].

            scores: np.ndarray
                These are the scores of each bounding box.

            labels: np.ndarray
                These are the labels of each bounding box. 0 represents barcodes
                and 1 represents QR codes.
        """
        height, width, _ = image.shape
        boxes, labels, scores = self.loaded_model.run_single_instance(image)
        
        # Filter bounding boxes based on the score threshold.
        indices = scores > self.parameters.acceptance_score
        boxes = boxes[indices, ...]
        scores = scores[indices]
        labels = labels[indices]

        # Scale boxes to be non-normalized to the image dimensions.
        boxes[..., 0] = boxes[..., 0] * width
        boxes[..., 1] = boxes[..., 1] * height
        boxes[..., 2] = boxes[..., 2] * width
        boxes[..., 3] = boxes[..., 3] * height
        boxes = boxes.astype(np.int16)

        return boxes, scores, labels

    def decode(self, image: np.ndarray) -> List[zxingcpp.Result]:
        """
        This method decodes barcodes and QR codes given a numpy image.

        Parameters
        ----------
            image: np.ndarray
                This is the image to pass to the barcode decoder.

        Returns
        -------
            decodes: list
                This list contains zxingcpp.Result objects with attributes
                text, format, content, position.
        """
        # Sharpen the image for better decoding.
        if self.parameters.sharpen > 0:
            image = sharpen_image(image, self.parameters.sharpen)
        return zxingcpp.read_barcodes(image)