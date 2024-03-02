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

"""The purpose of this module is to provide functions for object detection"""

import numpy as np
import torch

def yolo2xyxy(boxes: np.ndarray) -> np.ndarray:
    """
    This converts yolo annotation format into pascalvoc.

    Parameters
    ----------
        boxes: np.ndarray
            These are the bounding boxes in yolo format.

    Returns
    -------
        boxes: np.ndarray
            The bounding boxes in pascalvoc format.
    """
    w_c = boxes[..., 2:3]
    h_c = boxes[..., 3:4]
    boxes[..., 0:1] = boxes[..., 0:1] - w_c/2
    boxes[..., 1:2] = boxes[..., 1:2] - h_c/2
    boxes[..., 2:3] = boxes[..., 0:1] + w_c
    boxes[..., 3:4] = boxes[..., 1:2] + h_c
    return boxes

def batch_iou(box1, box2, eps: float=1e-7):
    """
    Performs a batch IoU for Tflite NMS detections.

    Parameters
    ----------  
        box1: torch.Tensor 
            (N,4) tensors containing bounding boxes.

        box1: torch.Tensor 
            (N,4) tensors containing bounding boxes.

        eps: float
            A minimal value to prevent division by zero.

    Returns
    -------
        iou: torch.Tensor 
            This contains an array of IoUs for each bounding box pair provided.
    """
    (a1,a2), (b1,b2) = box1.unsqueeze(1).chunk(2,2), box2.unsqueeze(0).chunk(2,2) 
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)
    return inter / ((a2-a1).prod(2) + (b2-b1).prod(2) - inter + eps)