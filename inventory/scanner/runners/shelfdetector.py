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

from inventory.scanner.kerasretinanet.models.tflite import TFliteRunner
import numpy as np


class ShelfDetector:
    """
    This class provides methods for detecting shelves using a 
    YoloV5 Tflite detection model.

    Parameters
    ----------
        model: str
            This is the path to the shelf detection model. Current
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
        This method performs shelf detections given a numpy image.

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
                These are the labels of each bounding box. 0 represents a 
                detected shelf.
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