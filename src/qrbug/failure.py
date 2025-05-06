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
    # Default values
    value                  : Optional[str]          = "VALEUR_NON_DEFINIE"
    display_type           : Optional[DisplayTypes] = DisplayTypes.text
    ask_confirm            : Optional[bool]         = True
    restricted_to_group_id : Optional[UserId]       = None

    def __init__(self, failure_id: FailureId):
        """
        Creates a new failure type.
        :param failure_id: The ID of this failure type.
        """
        super().__init__(failure_id)


def failure_update(failure_id: FailureId, **kwargs) -> Failure:
    """
    Creates a new failure type, or modifies an existing one.
    :param failure_id: The ID of this failure type.
    :param value: The value of this failure.
    :param display_type: How to display this failure ? Text, button, message box... ?
    :param ask_confirm: Whether the user will have to confirm when pressing the button.
    :param restricted_to_group_id: If only a single group can report this failure type.
    """
    return Failure.update_tree(failure_id, **kwargs)


def failure_add(failure_id: FailureId, child_failure_id: FailureId) -> None:
    """
    Adds a new child to an existing failure.
    :param failure_id: The ID of the failure to add the child to.
    :param child_failure_id: The ID of the child failure.
    """
    Failure.get(failure_id).add_child(Failure.get(child_failure_id))


def failure_remove(parent: FailureId, child: FailureId) -> None:
    """
    Removes the parenting link from a failure to another.
    :param parent: The ID of the failure to remove the child from.
    :param child: The ID of the failure to be removed.
    """
    Failure.get(parent).remove_child(Failure.get(child))
