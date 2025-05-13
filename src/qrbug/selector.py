from typing import Optional


class Selector:
    instances: dict[str, "Selector"] = {}

    def __init__(self, selector_id: str, expression: str):
        self.id = selector_id
        self.expression = expression
        self.instances[selector_id] = self

    def is_ok(self) -> bool:
        return eval(self.expression, {})

    def __class_getitem__(cls, selector_id: str) -> Optional["Selector"]:
        if selector_id in cls.instances:
            return cls.instances[selector_id]
        return None

def selector(selector_id: str, expression: str) -> Selector:
    return Selector(selector_id, expression)
