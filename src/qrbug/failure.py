"""
Defines all kinds of failures that can happen on a thing.
"""
from typing import Optional, TypeAlias
import enum

from qrbug.user import UserId
from qrbug.tree import Tree

FailureId: TypeAlias = str


class DisplayTypes(enum.Enum):
    text     = enum.auto()
    button   = enum.auto()
    redirect = enum.auto()
    input    = enum.auto()


class Failure(Tree):
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}

    # Default values
    value                  : Optional[str]          = "VALEUR_NON_DEFINIE"
    display_type           : Optional[DisplayTypes] = DisplayTypes.text
    ask_confirm            : Optional[bool]         = True
    restricted_to_group_id : Optional[UserId]       = None

    def _local_dump(self) -> str:
        return self.get_representation()


def failure_update(failure_id: FailureId, **kwargs) -> Failure:
    """
    Creates a new failure type, or modifies an existing one.
    :param failure_id: The ID of this failure type.
    :param value: The value of this failure.
    :param display_type: How to display this failure ? Text, button, message box... ?
    :param ask_confirm: Whether the user will have to confirm when pressing the button.
    :param restricted_to_group_id: If only a single group can report this failure type.
    """
    return Failure.update_attributes(failure_id, **kwargs)


def failure_add(parent: FailureId, child: FailureId) -> None:
    """
    Adds a new child to an existing failure.
    :param parent: The ID of the failure to add the child to.
    :param child: The ID of the child failure.
    """
    Failure.add_parenting_link(parent, child)


def failure_remove(parent: FailureId, child: FailureId) -> None:
    """
    Removes the parenting link from a failure to another.
    :param parent: The ID of the failure to remove the child from.
    :param child: The ID of the failure to be removed.
    """
    Failure.remove_parenting_link(parent, child)

if __name__ == "__main__":
    failure_update("0", value="Testing title", display_type=DisplayTypes.text)
    print(Failure.get("0").dump())
