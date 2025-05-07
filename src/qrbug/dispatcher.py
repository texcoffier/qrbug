from typing import Optional, TypeAlias

from qrbug.tree import Tree


class Dispatcher(Tree):
    instances: dict[str, "Dispatcher"] = {}

    # Default values
    action_id   :   Optional[str] = None
    selector_id :   Optional[str] = None
    group_id    :   Optional[str] = None
    when        :   Optional[str] = None


    def __init__(self, dispatch_id: str):
        """
        Creates a new dispatcher.
        :param dispatch_id: The ID of this dispatcher.
        """
        super().__init__(dispatch_id)


def dispatcher_update(dispatch_id: str, **kwargs) -> Dispatcher:
    """
    Creates a new dispatcher, or modifies an existing one.
    :param dispatch_id: The ID of this dispatcher.
    """
    return Dispatcher.update_tree(dispatch_id, **kwargs)


def dispatcher_del(dispatch_id: str) -> None:
    """
    Deletes an existing dispatcher.
    :param dispatch_id: The ID of this dispatcher.
    """
    del Dispatcher.instances[dispatch_id]
