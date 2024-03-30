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

from threading import Thread


class DataThread(Thread):
    """
    Inherits the python Thread module and provides a return value 
    to the target function.

    Parameters
    ----------
        The same parameters are involved with the Thread module.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        Thread.__init__(
            self, group=group, target=target, name=name, args=args, kwargs=kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, timeout=0.7):
        Thread.join(self)
        return self._return
