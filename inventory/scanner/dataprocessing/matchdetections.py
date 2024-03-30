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
from typing import Union

from inventory.scanner.runners.utils import (
    iou_2d,
    localize_distance
)
import numpy as np


class MatchDetections:
    """
    The purpose of this class is to match the model detections
    to the ground truth based on the highest IoU. This class also provides 

    Parameters
    ----------
        ground_truths: np.ndarray
            This is the bounding boxes of the detected packages which will
            be treated as ground truths.

        predictions: np.ndarray
            This is the bounding boxes of either the detected barcodes/QR codes
            or the texts which will be matched for each package.

        leniency_factor: int
            If the metric is centerpoint then matches can only be considered
            if the length of the diagonal of the bounding boxes does not exceed
            the number of times as the leniency factor when comparing against
            the center distance.

        metric: str
            The type of computation to use to measure how closely the 
            bounding boxes matches.

        group: bool
            This separates the extra indices into groups denoting that even
            though they were not matched, they may have IoUs greater than 0 to
            the ground truths that are matched. IoUs that are zero are kept
            as extra indices. 

    Raises
    ------
        IndexError
            Raised if duplicate matches were found in the final results or
            an invalid metric is passed. 
    """
    def __init__(
        self,
        ground_truths: np.ndarray,
        predictions: np.ndarray,
        leniency_factor: int=1,
        metric: str="iou",
        group: bool=False
    ) -> None:
        
        self._ground_truths = ground_truths
        self._predictions = predictions
        self.leniency_factor = leniency_factor
        self.metric = metric
        self.group = group

        # This contains the IoUs of each detection to ground truth match.
        self._iou_list = np.zeros(len(self._predictions))
        # An IoU map where rows are the ground truths and 
        # the predictions are the columns.
        self._iou_grid = np.zeros(
            (len(self._ground_truths), len(self._predictions)))
        # The matches containing ground truth and detection indices: 
        # [[dti, gti], [dti, gti], ..].
        self._index_matches = list()
        # The prediction indices that were not matched.
        self._index_unmatched_dt = list(range(0, len(self._predictions)))
        # The ground truth indices that were not matched.
        self._index_unmatched_gt = list(range(0, len(self._ground_truths)))
        # The unmatched detection, but with IoUs greater than 0 to an already matched ground truth.
        # [[detection indices], [...]] each list corresponds to the order of the ground truths.
        # This array has the same length as the packages array, and each element
        # contains the array indicating the indices of the texts for which
        # belongs to the package.
        self._index_unmatched_dt_grouped = list()

    @property
    def ground_truths(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the ground truths being matched.
        Can be set to :py:class:`list` or :py:class:`np.ndarray`

        Returns
        -------
            :py:class:`list` or :py:class:`np.ndarray`
                This is the ground truth list that denotes the package 
                bounding boxes. 
        """
        return self._ground_truths

    @ground_truths.setter
    def ground_truths(self, this_ground_truths: Union[list, np.ndarray]):
        """
        Sets the ground truth instance to matched.

        Parameters
        ----------
            this_ground_truths: :py:class:`list` or :py:class:`np.ndarray`
                This is the ground truth list that denotes the package 
                bounding boxes.  
        """
        self._ground_truths = this_ground_truths

    @property
    def predictions(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the predictions being matched.
        Can be set to :py:class:`list` or :py:class:`np.ndarray`

        Returns
        -------
            :py:class:`list` or :py:class:`np.ndarray`
                This is either the text detections or the barcode/QR code
                detections. 
        """
        return self._predictions

    @predictions.setter
    def predictions(self, this_predictions: Union[list, np.ndarray]):
        """
        Sets the predictions list to matched.

        Parameters
        ----------
            this_predictions: :py:class:`list` or :py:class:`np.ndarray`
                This is either the text detections or the barcode/QR code
                detections. 
        """
        self._predictions = this_predictions

    @property
    def index_matches(self) -> list[list[int, int]]:
        """
        Attribute to access the index_matches. This contains the indices
        of the ground truth and the predictions that are matched in the format
        [[gti, dti], [gti, dti], ...].
        Can be set to :py:class:`list`

        Returns
        -------
            :py:class:`list` 
                The indices of the matched ground truth and the predictions.
        """
        return self._index_matches

    @index_matches.setter
    def index_matches(self, this_index_matches: list[list[int, int]]):
        """
        Sets the index_matches.

        Parameters
        ----------
            this_index_matches: :py:class:`list` 
                These is the index_matches.
        """
        self._index_matches = this_index_matches

    @property
    def index_unmatched_dt(self) -> list[int]:
        """
        Attribute to access the index_unmatched_dt. This contains the indices
        of the predictions that were unmatched.
        Can be set to :py:class:`list`

        Returns
        -------
            :py:class:`list` 
                The indices of the unmatched predictions.
        """
        return self._index_unmatched_dt

    @index_unmatched_dt.setter
    def index_unmatched_dt(self, this_index_unmatched_dt: list[int]):
        """
        Sets the index_unmatched_dt.

        Parameters
        ----------
            this_index_unmatched_dt: :py:class:`list` 
                The indices of the unmatched predictions.
        """
        self._index_unmatched_dt = this_index_unmatched_dt

    @property
    def index_unmatched_dt_grouped(self) -> list[int]:
        """
        Attribute to access the index_unmatched_dt_grouped. This contains 
        the indices of the predictions that were unmatched but still contains
        IoU greater than 0 indicating it was matched previously matched to a 
        ground truth.
        Can be set to :py:class:`list`

        Returns
        -------
            :py:class:`list` 
                The indices of the unmatched predictions.
        """
        return self._index_unmatched_dt_grouped

    @index_unmatched_dt_grouped.setter
    def index_unmatched_dt_grouped(self, this_index_unmatched_dt_grouped: list[int]):
        """
        Sets the index_unmatched_dt_grouped.

        Parameters
        ----------
            this_index_unmatched_d_groupedt: :py:class:`list` 
                This contains the indices of the predictions that were 
                unmatched but still contains IoU greater than 0 indicating 
                it was matched previously matched to a ground truth.
        """
        self._index_unmatched_dt_grouped = this_index_unmatched_dt_grouped

    @property
    def index_unmatched_gt(self) -> list[int]:
        """
        Attribute to access the index_unmatched_gt. This contains the indices
        of the ground truths that were unmatched.
        Can be set to :py:class:`list`

        Returns
        -------
            :py:class:`list` 
                The indices of the unmatched ground truths.
        """
        return self._index_unmatched_gt

    @index_unmatched_gt.setter
    def index_unmatched_gt(self, this_index_unmatched_gt: list[int]):
        """
        Sets the index_unmatched_gt.

        Parameters
        ----------
            this_index_unmatched_gt: :py:class:`list` 
                The indices of the unmatched ground truths.
        """
        self._index_unmatched_gt = this_index_unmatched_gt

    @property
    def iou_list(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the iou_list. This contains the IoUs of the 
        matched predictions to ground truths.
        Can be set to :py:class:`list` or :py:class:`np.ndarray`

        Returns
        -------
            :py:class:`list` or :py:class:`np.ndarray`
                The IoU of the matched predictions to ground truths.
        """
        return self._iou_list

    @iou_list.setter
    def iou_list(self, this_iou_list: Union[list, np.ndarray]):
        """
        Sets the iou_list.

        Parameters
        ----------
            this_iou_list: :py:class:`list` or :py:class:`np.ndarray`
                The IoUs of matched predictions to ground truths.
        """
        self._iou_list = this_iou_list

    @property
    def iou_grid(self) -> Union[list, np.ndarray]:
        """
        Attribute to access the iou_grid. This contains all the IoU 
        computations where the rows are the ground truths and the columns
        are the predictions.
        Can be set to :py:class:`list` or :py:class:`np.ndarray`

        Returns
        -------
            :py:class:`list` or :py:class:`np.ndarray`
                The IoU combinations rows->ground truths, columns->predictions.
        """
        return self._iou_grid

    @iou_grid.setter
    def iou_grid(self, this_iou_grid: Union[list, np.ndarray]):
        """
        Sets the iou_grid.

        Parameters
        ----------
            this_iou_grid: :py:class:`list`  or :py:class:`np.ndarray`
                The IoU matrix.
        """
        self._iou_grid = this_iou_grid

    def match(self): #NOSONAR
        """
        The matching algorithm which matches the predictions to ground truth
        based highest IoU or lowest centerpoint distance between boxes.

        This algorithm incorporates recursive calls to 
        perform rematching of ground truth that were unmatched due to 
        duplicative matches, but the rematching is based on the next best IoU.

        Raises
        ------
            IndexError
                Raised if duplicate matches were found in the final results or
                an invalid metric is passed. 
        """
        if 0 in [len(self.ground_truths), len(self.predictions)]:
            return
    
        for gti, gt in enumerate(self.ground_truths):
            for dti, dt in enumerate(self.predictions):
                self.store_metric(gt, dt, gti, dti)
            if self.group:
                self.index_unmatched_dt_grouped.append(
                    np.squeeze(np.argwhere(self.iou_grid[gti] != 0)))
            # A potential match is the detection that produced the highest IoU.
            dti = np.argmax(self.iou_grid[gti])
            iou = max(self.iou_grid[gti])
            self.compare_matches(dti, gti, iou)

        # Find the unmatched predictions
        for match in self.index_matches:
            self.index_unmatched_dt.remove(match[0])
            self.index_unmatched_gt.remove(match[1])

    def compare_matches(self, dti: int, gti: int, iou: float):
        """
        Checks if duplicate matches exists. A duplicate match is when the 
        same detection is being matched to more than one ground truth. 
        The IoUs are compared and the better IoU is the true match and the 
        ground truth of the other match is then rematch to the next best IoU, 
        but it performs a recursive call to check if the next best IoU 
        also generates a duplicate match.

        Parameters
        ----------
            dti: int
                The detection index being matched to the current ground truth.

            gti: int
                The current ground truth matched to the detection.

            iou: float
                The current best IoU that was computed for the current ground
                truth against all detections.

        Raises
        ------
            IndexError:
                Raised if a duplicate match was left unchecked 
                and was not rematched. 
        """
        twice_matched = [(d, g) for d, g in self.index_matches if d == dti]
        if len(twice_matched) == 1:
            # Compare the IoUs between duplicate matches.
            dti, pre_gti = twice_matched[0]
            if iou > self.iou_list[dti]:
                self.index_matches.remove((dti, pre_gti))
                self.iou_list[dti] = iou
                self.index_matches.append((dti, gti))

                # Rematch pre_gti
                self.iou_grid[pre_gti][dti] = 0.
                dti = np.argmax(self.iou_grid[pre_gti])
                iou = max(self.iou_grid[pre_gti])
                if iou > 0:
                    self.compare_matches(dti, pre_gti, iou)
            else:
                # Rematch gti
                self.iou_grid[gti][dti] = 0.
                dti = np.argmax(self.iou_grid[gti])
                iou = max(self.iou_grid[gti])
                if iou > 0:
                    self.compare_matches(dti, gti, iou)

        elif len(twice_matched) == 0:
            if iou > 0:
                self.iou_list[dti] = iou
                self.index_matches.append((dti, gti))
        else:
            raise IndexError("Duplicate matches were unchecked.")

    def store_metric(
        self,
        gt: Union[list, np.ndarray],
        dt: Union[list, np.ndarray],
        gti: int,
        dti: int
    ):
        """
        Computes either the 3D or 2D IoU or centerpoint distances 
        and stores the values in the IoU grid.

        When the iou_first flag is False, IoU is 
        considered 0 if the classes don't match.

        Parameters
        ----------
            gt: list or np.ndarray
                This contains ground truth bounding boxes. 

            dt: list or np.ndarray
                This contains prediction bounding boxes.

            gti: int
                This is the index of the ground truth 
                bounding boxes.

            dti: int 
                This is the index of the prediction 
                bounding boxes.

        Raises
        ------
            ValueError
                Raised if an invalid metric is passed. 
        """
        if self.metric == "iou":
            self.iou_grid[gti][dti] = \
                iou_2d(dt.astype(float),
                        gt.astype(float))

        elif self.metric == "centerpoint":
            self.iou_grid[gti][dti] = 1 - localize_distance(
                dt.astype(float),
                gt.astype(float),
                leniency_factor=self.leniency_factor
            )
        else:
            raise ValueError(
                "Unknown matching matching metric specified.")