import time
from typing import Callable, Awaitable

import qrbug

class ActionReturnValue:
    """
    What is returned by an action.
    """
    def __init__(self, error_msg: str = '', info_msg: str = ''):
        self.error_msg = error_msg
        self.info_msg = info_msg

    def is_empty(self):
        return self.error_msg == '' and self.info_msg == ''

    def __bool__(self):
        return not self.is_empty()
