from typing import Optional, TypeAlias

from qrbug.tree import Tree


DispatcherId: TypeAlias = str


class Dispatcher(Tree):
    instances: dict[DispatcherId, "Dispatcher"] = {}

    # Default values
    action_id   :   Optional[str] = None
    selector_id :   Optional[str] = None
    group_id    :   Optional[str] = None
    when        :   Optional[str] = None

    def _local_dump(self) -> str:
        return self.get_representation()


def dispatcher_update(dispatch_id: str, **kwargs) -> Dispatcher:
    """
    Creates a new dispatcher, or modifies an existing one.
    :param dispatch_id: The ID of this dispatcher.
    """
    return Dispatcher.update_attributes(dispatch_id, **kwargs)


def dispatcher_del(dispatch_id: str) -> None:
    """
    Deletes an existing dispatcher.
    :param dispatch_id: The ID of this dispatcher.
    """
    del Dispatcher.instances[dispatch_id]

if __name__ == "__main__":
    dispatcher_update("0", when="Test", selector_id="0")
    print(Dispatcher.get("0").dump())
