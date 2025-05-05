"""
Defines all kinds of failures that can happen on a thing.
"""
from typing import Optional, TypeAlias
import enum

FailureId: TypeAlias = str


class DisplayTypes(enum.Enum):
    text = enum.auto()
    button = enum.auto()
    redirect = enum.auto()
    input = enum.auto()


class Failure:
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}  # Maps every failure ID to a failure instance

    # Default values
    value: Optional[str] = "VALEUR_NON_DEFINIE"
    display_type: Optional[DisplayTypes] = DisplayTypes.text
    ask_confirm: Optional[bool] = True
    restricted_to_group_id: Optional[str] = None

    def __init__(self, failure_id: FailureId):
        """
        Creates a new failure type.
        :param failure_id: The ID of this failure type.
        """
        self.failure_id = failure_id
        self.child_failures: list[FailureId] = []  # the IDs of the children of this failure

    def add_child(self, child: "Failure") -> None:
        """
        Adds a new child to this failure.
        :param child: Another failure.
        """
        assert child.failure_id not in self.child_failures, f"{child.failure_id} is already a child of {self.failure_id}"
        assert child.failure_id != self.failure_id, f"Cannot make {child.failure_id} a child of itself !"
        self.child_failures.append(child.failure_id)

    @classmethod
    def get(cls, failure_id: FailureId) -> "Failure":
        """
        Returns the failure at the given ID.
        **Warning :** If the failure doesn't exist, a brand new one is created.
        :param failure_id: The ID of this failure.
        :return: The failure at the given ID.
        """
        if failure_id not in Failure.instances:
            Failure.instances[failure_id] = Failure(failure_id)
        return Failure.instances[failure_id]


def failure_update(failure_id: FailureId, **kwargs) -> Failure:
    """
    Creates a new failure type, or modifies an existing one.
    :param failure_id: The ID of this failure type.
    :param value: The value of this failure.
    :param display_type: How to display this failure ? Text, button, message box... ?
    :param ask_confirm: Whether the user will have to confirm when pressing the button.
    :param restricted_to_group_id: If only a single group can report this failure type.
    """
    # Gets the failure the user asked for (or creates one with the corresponding ID if it did not exist)
    failure = Failure.get(failure_id)

    # Sets the new data of the failure if it is set
    for arg, value in kwargs.items():
        if hasattr(Failure, arg) and arg != "instances":
            setattr(failure, arg, value)

    return failure


def failure_add(failure_id: FailureId, child_failure_id: FailureId) -> None:
    """
    Adds a new child to an existing failure.
    :param failure_id: The ID of the failure to add the child to.
    :param child_failure_id: The ID of the child failure.
    """
    Failure.get(failure_id).add_child(Failure.get(child_failure_id))
