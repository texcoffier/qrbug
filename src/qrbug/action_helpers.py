import time
from typing import Callable, Awaitable

import qrbug


def auto_close_incident(action_function: Callable[[qrbug.Incident, "aiohttp.web.Request"], Awaitable[None]]):
    """
    Helper decorator for actions : Auto-closes the given incident.
    """
    async def wrapper(incident: qrbug.Incident, request: "aiohttp.web.Request") -> None:
        await action_function(incident, request)
        qrbug.Incident.close(incident.thing_id, incident.failure_id, request.remote, '')
    return wrapper


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
