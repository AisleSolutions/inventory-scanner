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

from typing import Union
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

def iou_2d(
    box_a: Union[list, np.ndarray], 
    box_b: Union[list, np.ndarray], 
    eps: float=1e-10
) -> float:
    """
    Computes the IoU between ground truth and detection 
    bounding boxes. IoU computation method retrieved from:: 
    https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
    
    Parameters
    ----------
        box_a: list or np.ndarray
            This is a bounding box [xmin, ymin, xmax, ymax].
        
        box_b: list or np.ndarray
            This is a bounding box [xmin, ymin, xmax, ymax].

    Returns
    -------
        IoU: float
            The IoU score between boxes.

    Exceptions
    ----------
        ValueError
            Raised if the provided boxes for ground truth 
            and detection does not have a length of four.

        Raised if the calculated IoU is invalid. 
            i.e. less than 0 or greater than 1.
    """
    if len(box_a) != 4 or len(box_b) != 4:
        raise ValueError("The provided bounding boxes does not meet " \
                            "expected lengths [xmin, ymin, xmax, ymax]")
    
    # Determine the (x, y)-coordinates of the intersection rectangle.
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    # Compute the area of intersection rectangle.
    inter_area = max((x_b - x_a, 0)) * max((y_b - y_a), 0)
    if inter_area == 0:
        return 0.
    # Compute the area of both the prediction and ground-truth rectangles.
    box_a_area = abs((box_a[2] - box_a[0]) * (box_a[3] - box_a[1]))
    box_b_area = abs((box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))

    # Compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = inter_area / float(box_a_area + box_b_area - inter_area)

    if iou > 1. + eps or iou < 0.:
        raise ValueError(iou)
    # Return the intersection over union value.
    return iou  

def minkowski_distance(
    center_a: Union[list, np.ndarray], 
    center_b: Union[list, np.ndarray],
    p: int=2
) -> float:
    """
    Calculates the Minkowski distance between two points. 
    If p is 1, then this would be the Hamming distance.
    If p is 2, then this would be the Euclidean distance.
    https://www.analyticsvidhya.com/blog/2020/02/4-types-of-distance-metrics-in-machine-learning/

    Parameters
    ----------
        center_a: list or np.ndarray
            The 2D [x,y] or 3D [x,y,z] coordinates 
            for the first point.

        center_b: list or np.ndarray
            The 2D [x,y] or 3D [x,y,z] coordinates 
            for the second point.

        p: int
            The order in the minkowski distance computation.

    Returns
    -------
        distance: float
            The distance between two points.
    """
    return np.power(np.sum(np.power(np.absolute(center_a-center_b), p)), 1/p)

def get_center_point(box: Union[list, np.ndarray]) -> np.ndarray:
    """
    If given the [xmin, ymin, xmax, ymax] of the bounding box,
    this function finds the centerpoint of the bounding box in [x,y].

    Parameters
    ----------
        box: list or np.ndarray
            The [xmin, ymin, xmax, ymax] of the bounding box.

    Returns
    -------
        The centerpoint coordinate [x,y].
    """
    width = box[2] - box[0]
    height = box[3] - box[1]
    return np.array([box[0] + width/2, box[1] + height/2])

def localize_distance(
    box_a: Union[list, np.ndarray], 
    box_b: Union[list, np.ndarray], 
    leniency_factor: int=2
):
    """
    Given the diagonal of the smaller bounding box, the center distance 
    between the bounding boxes will only be considered if the diagonal length 
    does not exceed the number of times as the leniency factor when compared
    against the center distance calculated.

    Parameters
    ----------
        box_a: list or np.ndarray
            This is a bounding box [xmin, ymin, xmax, ymax].
        
        box_b: list or np.ndarray
            This is a bounding box [xmin, ymin, xmax, ymax].

        leniency_factor: int
            This is the maximum times the diagonal of the smaller bounding
            box should fit inside the center distances.

    Returns
    -------
        distance: float
            The restricted distance between the centers of bounding boxes. If
            it does not meet the leniency criteria, it will return the maximum
            distance of 1.
    """
    diagonal = min(
        minkowski_distance(box_a[0:2], box_a[2:4]), 
        minkowski_distance(box_b[0:2], box_b[2:4]))
    center_distance = minkowski_distance(box_a, box_b)
    if int(center_distance/diagonal) <= leniency_factor:
        return center_distance
    # Validation takes 1-center_distance, so returning 1. would indicate far apart.
    return 1. 