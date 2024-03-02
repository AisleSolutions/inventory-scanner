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

#from sensor_msgs.msg import LaserScan

class ScanManager:

    vector : list[LidarScan] = list() # List of all passed-in scans.
    
    """
    Stores the scan of the Lidar at a particular location. The scan should
    either be in the x-y plane (scanning surroundings) or the 
    x-z plane (scanning vertically)
    """

    
    def __init__(self, header:Header) -> None:
        
        # Options should be "xy" (scanning surroundings) or "xz" (scanning vertically).
        self._orientation = "xy"

        # TODO: Implement this class along with its properties.
    
    @staticmethod
    def polar2cartesian():
        """
        This method converts scans in polar coordinate systems into cartesian
        form.
        """
        # TODO: Implement this method.

    def localize():
        """
        This is likely going to be handled by a mapping utility. Returns current location on a point-cloud informed floor map.
        """
        # TODO: Implement this method.

    def count_items():
        """
        If it is concerns the Lidar is directly facing a shelf, this method
        should analyze the scan readings to gather a package count based
        on the scans.
        """
        # TODO: Implement this method.