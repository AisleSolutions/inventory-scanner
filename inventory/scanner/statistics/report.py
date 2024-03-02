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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from inventory.scanner.statistics import PackageCount

class Report:
    """
    This class transforms the package count statistics into a report
    such as an Excel file and provides PostGreSQL methods to upload the report
    into the Django service for display and further analysis.
    """

    def __init__(
            self,
            package_count: PackageCount
        ) -> None:
        pass

    # TODO: Implement method to transform the package count data into a report.
    # TODO: Implement method to upload the report to a Django service.