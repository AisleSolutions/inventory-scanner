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
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from inventory.scanner.runners import Parameters

from inventory.scanner.dataprocessing.utils import (
    validate_path,
    preprocess_image,
    resize
)
from inventory.scanner.kerasretinanet import models
import numpy as np


class PackageDetector:
    """
    This class provides methods for detecting packages in an image.

    Parameters
    ----------
        model: str
            This is the path to the package detection model. Current models 
            supported are Keras Retinanet models with .h5 extension.

        parameters: Parameters
            This contains model parameters.
    """
    def __init__(
            self,
            model: str,
            parameters: Parameters
        ) -> None:

        self.model = validate_path(model)
        self.loaded_model = models.load_model(self.model)
        self.parameters = parameters

    def detect(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        This method performs package detections given a numpy image.

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
                These are the labels of each bounding box. For keras_retinanet,
                the labels are always 0.
        """
        
        # min_side and max_side is default provided in the keras_retinanet example.
        image, scale = resize(image, min_side=800, max_side=1333)
        image = preprocess_image(image)

        boxes, scores, labels, _ = self.loaded_model.predict_on_batch(
            np.expand_dims(image, axis=0))
        
        # Filter bounding boxes based on the score threshold.
        indices = scores[0] > self.parameters.acceptance_score
        boxes = boxes[0][indices, ...]
        scores = scores[0][indices]
        labels = labels[0][indices]

        # Correct image scaling.
        boxes /= scale

        return boxes, scores, labels
