class Selector:
    instances: dict[str, "Selector"] = {}

    def __init__(self, selector_id: str, expression: str):
        self.id = selector_id
        self.expression = expression
        self.instances[selector_id] = self

def selector(selector_id: str, expression: str) -> Selector:
    return Selector(selector_id, expression)
