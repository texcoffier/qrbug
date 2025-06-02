import time
from typing import Callable, Awaitable

import qrbug


def auto_close_incident(action_function: Callable[[qrbug.Incident, "aiohttp.web.Request"], Awaitable[None]]):
    """
    Helper decorator for actions : Auto-closes the given incident.
    """
    async def wrapper(incident: qrbug.Incident, request: "aiohttp.web.Request") -> None:
        await action_function(incident, request)
        qrbug.append_line_to_journal(f"incident_del({repr(incident.thing_id)}, {repr(incident.failure_id)}, {repr(request.remote)}, {int(time.time())}, '')\n")
    return wrapper
