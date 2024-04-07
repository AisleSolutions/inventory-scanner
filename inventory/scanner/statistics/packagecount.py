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


class PackageCount:
    """
    This class stores the unique package statistics.

    Parameters
    ----------
        label: str
            The label of this package object.
    """
    def __init__(self, label: str="Unlabeled") -> None:
        self._label = label
        self._count = 0
        self._boxes = list()
        self._descriptors = list()

    @property
    def label(self) -> str:
        """
        Attribute to access the label of the package.
        Can be set to :py:class:`str`

        Returns
        -------
            :py:class:`str`: The label of the package.
        """
        return self._label
    
    @label.setter
    def label(self, this_label: str):
        self._label = this_label

    @property
    def count(self) -> int:
        """
        Attribute to access the package count.
        Can be set to :py:class:`int`

        Returns
        -------
            :py:class:`int`: The package count
        """
        return self._count
    
    def increment_count(self, add: int = 1):
        """
        Adds the current count of the packages.

        Parameters
        ----------
            add: int
                The value to add to the count.
        """
        self._count += add

    @property
    def boxes(self) -> list:
        """
        Attribute to access the package bounding boxes.
        Can be set to :py:class:`list`

        Returns
        -------
            :py:class:`list` The package bounding boxes.
        """
        return self._boxes
    
    @boxes.setter
    def boxes(self, this_boxes: list):
        self._boxes = this_boxes

    @property
    def descriptors(self) -> list:
        """
        Attribute to access the package text descriptors.
        Can be set to :py:class:`list`

        Returns
        -------
            :py:class:`list` The package text descriptors.
        """
        return self._descriptors
    
    @descriptors.setter
    def descriptors(self, this_descriptors: list):
        self._descriptors = this_descriptors
