class Action:
    instances: dict[str, "Action"] = {}

    def __init__(self, action_id: str, python_script: str):
        self.id = action_id
        self.python_script = python_script
        self.instances[action_id] = self

def action(action_id: str, python_script: str) -> Action:
    return Action(action_id, python_script)
