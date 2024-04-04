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
    from inventory.scanner.dataprocessing import ProcessCount
    from inventory.scanner.coordination import Coordinator

from inventory.scanner.dataprocessing import ShelfImage
from inventory.scanner import logger

try:
    import cv2
except ImportError:
    logger(
        "OpenCV is not installed which is required for OpenCV streaming.", 
        code="WARNING")

class OpenCVStreamer:
    """
    This class provides methods for running the video stream using OpenCV.

    Parameters
    ----------
        source: int
            This is the index of the camera source to use.

        count_processor: ProcessCount
            This is the object to process the frames for package counts.
        
        coordinator: Coordinator
            This is the object to handle device coordination to face the shelf.

        fps: int
            This is the frames per second to operate the stream.

        resolution: tuple
            This is the (width, height) resolution of each frame.

        show: bool
            Set this condition to True to show the frames with bounding box
            overlays for sanity checking of the detections.
    """
    def __init__(
            self,
            source: int=0,
            count_processor: ProcessCount=None,
            coordinator: Coordinator=None,
            fps: int=30,
            resolution: tuple=(1920, 1080),
            show: bool=False
        ) -> None:
        self.source = source
        self.count_processor = count_processor
        self.coordinator = coordinator
        self._scan = True
        self.shelf_image = ShelfImage()

        self.cap = self.open_camera(source)
        #self.cap = self.setup_cap(self.cap, resolution, fps) #NOSONAR
        self.show = show
        if not (self.wait_for_cam()):
            logger(
                "Camera was not able to capture frames while initializing.",
                code="ERROR")
            
    @property
    def scan(self) -> bool:
        """
        Access the scan condition property.

        Returns
        -------
            scan: bool
                This is the condition whether to perform the inventory
                scanning process for counting.

                If this is False, this means the robot/device is still
                performing alignment to the shelves.
        """
        return self._scan
    
    @scan.setter
    def scan(self, new_scan: bool):
        """
        Set a new condition to the scanning property.

        Parameters
        ----------
            new_scan: bool  
                This property determines whether or not to perform inventory
                scanning.
        """
        self._scan = new_scan

    @staticmethod
    def open_camera(source: int=0):
        """
        Initializes the camera feed.

        Parameters
        ----------
            source: int
            This is the index of the camera source to use.

        Returns
        -------
            cap: cv2.VideoCapture
                Provides OpenCV video capturing functionalities.
        """
        try:
            cap = cv2.VideoCapture(source)
        except NameError:
            logger(
                "OpenCV is required for streaming. Please see README.md for installation instructions",
                code="ERROR")
        return cap
    
    @staticmethod
    def setup_cap(cap, resolution: tuple=(1920,1080), fps: int=30):
        """
        Provides initializes of the VideoCapturing object with resolution
        and fps settings.

        Parameeters
        -----------
            cap: cv2.VideoCapture
                Provides OpenCV video capturing functionalities.

            resolution: tuple
                This is the (width, height) resolution of each frame.

            fps: int
                This is the frames per second to operate the stream.

        Returns
        -------
            cap: cv2.VideoCapture
                Provides OpenCV video capturing functionalities.
        """
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        cap.set(cv2.CAP_PROP_FPS, fps)
        return cap
    
    def wait_for_cam(self) -> bool:
        """
        Waits for the camera to initializes and verifies that the frames can be
        captured.

        Returns
        -------
            check: bool
                If this is True, then the camera was initialized properly and 
                frame can be captured.
        """
        for _ in range(30):
            check = self.on_new_sample()
        return check
    
    def on_new_sample(self) -> bool:
        """
        Pulls one frame sample and processes the frame to count 
        packages captured.

        Returns
        -------
            If this is True, then the frame was successfully captured.
        """
        ret, image = self.cap.read()
        if ret:
            if self.scan:
                # To perform stitching, pass `self.shelf_image` instead.
                image = self.count_processor.process(image)
                self.scan = False
            else:
                # Perform motor commands to align the robot.
                image, has_shelving = self.coordinator.process(image)
                # If the camera sees shelving, then store the images to stitch.
                if has_shelving:
                    # This code stores the shelving to be stitched.
                    #self.shelf_image._shelf_segments.append(image)
                    self.scan = True
                # Once the camera stops seeing shelving, start scanning.
                else:
                    self.scan = False

            if self.show:
                cv2.imshow("frame", image)
        return ret

    def run(self):
        """
        This method runs the OpenCV streaming applications.
        """
        while True:
            if not(self.on_new_sample()):
                self.release()
                logger(
                    "Camera frame capture was not successful.", 
                    code="ERROR")
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger(
                    "Ending streaming process.", 
                    code="INFO"
                )
                break
        self.release()

    def release(self):
        """
        This method closes resources before ending the application.
        """
        self.cap.release()
        cv2.destroyAllWindows()
