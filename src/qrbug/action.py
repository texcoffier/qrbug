import time
from pathlib import Path
from typing import TypeAlias, Optional, Callable, Awaitable

import qrbug

ActionId: TypeAlias = str
ACTIONS_FOLDER = Path('ACTIONS/')


class Action:
    instances: dict[ActionId, "Action"] = {}

    def __init__(self, action_id: ActionId, python_script: str):
        self.id = action_id
        self.python_script = python_script
        if not self.python_script.endswith('.py'):
            raise Exception(f'"{self.python_script}" is not a Python file')
        self.instances[action_id] = self

    async def run(self, incident: qrbug.Incident, request) -> Optional[str]:
        module_vars = qrbug.exec_code_file(ACTIONS_FOLDER / self.python_script, {"Incident": qrbug.Incident})
        # We assume that the run function is present in the action so the
        # server throws an exception if it is not the case
        return await module_vars['run'](incident, request)

    def __class_getitem__(cls, action_id: ActionId) -> Optional["Action"]:
        return cls.instances.get(action_id, None)


def action(action_id: str, python_script: str) -> Action:
    return Action(action_id, python_script)


def auto_close_incident(action_function: Callable[[qrbug.Incident, "aiohttp.web.Request"], Awaitable[None]]):
    """
    Helper decorator for actions : Auto-closes the given incident.
    """
    async def wrapper(incident: qrbug.Incident, request: "aiohttp.web.Request") -> None:
        await action_function(incident, request)
        qrbug.append_line_to_journal(f"incident_del({repr(incident.thing_id)}, {repr(incident.failure_id)}, {repr(request.remote)}, {int(time.time())}, '')\n")
    return wrapper


qrbug.Action = Action
qrbug.action_update = action
qrbug.ActionId = ActionId

if __name__ == '__main__':
    action('test', 'test.py')
    #Action['test'].run()
