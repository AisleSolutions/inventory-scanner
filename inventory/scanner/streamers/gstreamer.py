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

from inventory.scanner import logger

try:
    import gi
    gi.require_version("Gst", "1.0")
    gi.require_version("GstApp", "1.0")
    from gi.repository import Gst, GstApp, GLib
except ImportError:
    logger(
        "GStreamer is not installed which is required for GStreamer streaming.", 
        code="WARNING")

import numpy as np

class GStreamer:
    """
    This class provides methods for running GStreamer.

    Parameters
    ----------
        source: str
            This is the camera source to capture frames.

        count_processor: ProcessCount
            This is the object to process the frames for package counts.

        coordinator: Coordinator
            This is the object to handle device coordination to face the shelf.
    """
    def __init__(
            self,
            source: str="/dev/video0",
            count_processor: ProcessCount=None,
            coordinator: Coordinator=None,
        ) -> None:
        self.source = source
        self._scan = False
        self.count_processor = count_processor
        self.coordinator = coordinator

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
    def on_new_sample(
        app_sink, 
        count_processor: ProcessCount, 
        coordinator: Coordinator, 
        scan: bool
    ) -> bool:
        """
        This method pulls samples from the appsink.

        Parameters
        ----------
            app_sink: gi.repository.GstApp.AppSink
                GStreamer sink to forward samples.

            count_processor: ProcessCount
            This is the object to process the frames for package counts.

            coordinator: Coordinator
                This is the object to handle device coordination to face the shelf.

            scan: bool
                Specify to perform inventory scanning, otherwise, device 
                coordination is still in process.

        Returns
        -------
            True: Stop streaming.
            False: Continue streaming.
        """
        sample = app_sink.pull_sample()

        buffer = sample.get_buffer()
        caps = sample.get_caps()
        height = caps.get_structure(0).get_value('height')
        width = caps.get_structure(0).get_value('width')
        channels = 3

        image = np.ndarray(
                (height, width, channels),
                buffer=buffer.extract_dup(0, buffer.get_size()),
                dtype=np.uint8)
        
        if scan:
            image, ret = count_processor.process_codes(image)
        else:
            image, ret = coordinator.process(image)

        # If ret = True, return False meaning streaming continues.
        return not ret
    
    def run(self):
        """
        This method runs the GStreamer application.
        """
        # This is needed to expose the app_sink.pull_sample() function.
        _ = GstApp

        Gst.init(None)
        
        pipeline = Gst.parse_launch("""
            v4l2src device=%s !
            queue !
            decodebin ! videoconvert ! video/x-raw, format=RGB !
            appsink sync=true max-buffers=1 drop=true name=sink emit-signals=true
        """ % (self.source))

        loop = GLib.MainLoop()
        appsink = pipeline.get_by_name("sink")
        
        appsink.connect("new-sample",
                        self.on_new_sample,
                        self.count_processor,
                        self.coordinator,
                        self.scan
                    )
        
        pipeline.set_state(Gst.State.PLAYING)
        loop.run()
        
        pipeline.set_state(Gst.State.NULL)
        loop.quit()
