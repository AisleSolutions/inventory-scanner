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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from inventory.scanner.runners import Parameters

from inventory.scanner.dataprocessing.utils import (
    draw_bounding_box,
    draw_text
)
from PIL import Image, ImageDraw
import numpy as np


class Coordinator:
    """
    This class implements the algorithm for coordinating the device
    to face the shelves.

    Parameters
    -----------
        path_package_model: str
            This is the path to the package detection model.

        path_identification model: str
            This is the path to the model that detects barcodes and QR codes.

        parameters: Parameters
            This contains the model parameters to control the model's
            behaviour.

        show: bool
            Specify whether to show the image with overlain bounding boxes
            of the detections.
    """
    def __init__(
            self,
            path_shelf_model: str,
            parameters: Parameters,
            show: bool=False
        ) -> None:
        
        from inventory.scanner.runners import ShelfDetector
        self.shelf_detector = ShelfDetector(
            model=path_shelf_model,
            parameters=parameters
        )
        self.show = show

    def process(self, image: np.ndarray):
        """
        """
        boxes, scores, labels = self.shelf_detector.detect(image)

        if self.show:
            image_drawn = Image.fromarray(image)
            image_draw = ImageDraw.Draw(image_drawn)

        for box, score, label in zip(boxes, scores, labels):
            if self.show:
                draw_bounding_box(
                    image_draw, ((box[0], box[1]), (box[2], box[3])))
                
            if self.show:
                if label == 0:
                    text = f"Shelf {round(score*100, 2)}"
                else:
                    text = f"{label} {round(score*100, 2)}"

            draw_text(image_draw, text, (box[0], box[1]-10), color="white")
        
        if self.show:
            image = np.asarray(image_drawn)

        return image, True