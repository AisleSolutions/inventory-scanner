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

from importlib.metadata import version as pkgver

def version() -> str:
    """
    Return the current version of the project.

    Returns
    -------
        version: str
            This is the current version of the project.
    """
    try:
        return pkgver('inventory-scanner')
    except Exception:
        from subprocess import Popen, PIPE
        from re import sub
        pipe = Popen('git describe --tags --always', stdout=PIPE, shell=True)
        ver = str(pipe.communicate()[0].rstrip().decode("utf-8"))
        ver = str(sub(r'-g\w+', '', ver))
        return ver.replace('-', '.post')
    
def logger(message: str, code: str="INFO"):
    """
    Logs messages on the terminal. The following codes are
    accepted:

    Parameters
    ----------
        message: str
            The message to print.

        code: str
            The message type. These codes are accepted "ERROR", "WARNING", 
            "INFO", "SUCCESS".
    """
    if code.lower() == "error":
        print(f"\t - [ERROR]: {message}")
        exit(1)
    elif code.lower() == "warning":
        print(f"\t - [WARNING]: {message}")
    elif code.lower() == "info":
        print(f"\t - [INFO]: {message}")
    elif code.lower() == "success":
        print(f"\t - [SUCCESS]: {message}")
    else:
        print(f"\t - {message}")