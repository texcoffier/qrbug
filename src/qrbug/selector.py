from typing import Optional

import qrbug


class Selector:
    instances: dict[str, "Selector"] = {}

    def __init__(self, selector_id: str, expression: str):
        self.id = selector_id
        self.expression = expression
        self.instances[selector_id] = self

    def is_ok(self, user: 'qrbug.User', thing: 'qrbug.Thing', failure: 'qrbug.Failure') -> bool:
        return eval(self.expression, {"user": user, "thing": thing, "failure": failure})

    def __class_getitem__(cls, selector_id: str) -> Optional["Selector"]:
        return cls.instances.get(selector_id, None)


def selector(selector_id: str, expression: str) -> Selector:
    return Selector(selector_id, expression)


qrbug.Selector = Selector
qrbug.selector_update = selector
