from pathlib import Path
from typing import TypeAlias, Optional, List

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

    async def run(self, incidents: List[qrbug.Incident], request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
        module_vars = qrbug.exec_code_file(ACTIONS_FOLDER / self.python_script, {"Incident": qrbug.Incident})
        # We assume that the run function is present in the action so the
        # server throws an exception if it is not the case
        return await module_vars['run'](incidents, request)

    def __class_getitem__(cls, action_id: ActionId) -> Optional["Action"]:
        return cls.instances.get(action_id, None)


def action(action_id: str, python_script: str) -> Action:
    return Action(action_id, python_script)


qrbug.Action = Action
qrbug.action_update = action
qrbug.ActionId = ActionId

if __name__ == '__main__':
    action('test', 'test.py')
    #Action['test'].run()
