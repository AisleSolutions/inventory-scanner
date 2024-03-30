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

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from autocorrect import Speller
from typing import Tuple
import numpy as np
import easyocr
import re


class TextDetector:
    """
    This class detects texts given an image.
    """
    def __init__(self) -> None:
        
        # This object detects texts in images.
        self.reader = easyocr.Reader(['ch_sim','en']) 
        # This object corrects the spelling in texts.
        self.speller = Speller(lang='en')

    def detect(self, image: np.ndarray) -> Tuple[list, list, list]:
        """
        This method detects and decodes text. For each text, remove special 
        characters, lower case, and check for spelling. Check if the words 
        exists in the english dictionary.

        Parameters
        ----------
            image: np.ndarray
                This is the numpy array image.

        Returns
        -------
            boxes: list
                This contains the [[xmin, ymin, xmax, ymax], [...]] locations
                of each text.

            scores: list
                This contains the confidence scores of each text.

            texts: list
                This contains the string text detections.
        """
        height, width, _ = image.shape
        boxes, scores, texts = list(), list(), list()
        detections = self.reader.readtext(image)
        if detections is None:
            return boxes, scores, texts

        for detection in detections:
            box, text, score = detection
            # Remove special characters and convert to lower characters.
            text = re.sub('\W+','', text).lower()
            # Autocorrect spelling.
            text = self.speller(text)

            if text in ["", " "]:
                continue

            # Check if the text is a valid word.
            if score > 0.08:
                # Store in the format [xmin, ymin, xmax, ymax].
                box = [
                    box[0][0], 
                    box[0][1], 
                    box[2][0],
                    box[2][1]
                ]
                boxes.append(box)
                scores.append(score)
                texts.append(text)
        
        boxes = np.array(boxes)
        boxes[..., 0] = boxes[..., 0] / width
        boxes[..., 1] = boxes[..., 1] / height
        boxes[..., 2] = boxes[..., 2] / width
        boxes[..., 3] = boxes[..., 3] / height
        scores = np.array(scores)

        return boxes, scores, texts