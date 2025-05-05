"""
Defines all kinds of failures that can happen on a thing.
"""
from typing import Optional, TypeAlias

FailureId: TypeAlias = str


class Failure:
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}  # Maps every failure ID to a failure instance

    def __init__(self, failure_id: FailureId):
        """
        Creates a new failure type.
        :param failure_id: The ID of this failure type.
        """
        self.failure_id = failure_id
        self.title = title
        self.display_type = display_type
        self.ask_confirm = ask_confirm
        self.restricted_to_group_id = restricted_to_group_id
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


def failure(failure_id: FailureId, title: Optional[str] = None, display_type: Optional[str] = None,
            ask_confirm: Optional[bool] = None, restricted_to_group_id: Optional[str] = None) -> Failure:
    """
    Creates a new failure type, or modifies an existing one.
    :param failure_id: The ID of this failure type.
    :param title: The title of this failure (short).
    :param display_type: How to display this failure ? Text, button, message box... ?
    :param ask_confirm: Whether the user will have to confirm when pressing the button.
    :param restricted_to_group_id: If only a single group can report this failure type.
    """
    # Gets the failure the user asked for (or creates one with the corresponding ID if it did not exist)
    given_failure = Failure.get(failure_id)

    # Sets the new data of the failure if it is set
    # TODO: Better way ?
    if title is not None:
        given_failure.title = title
    if display_type is not None:
        given_failure.display_type = display_type
    if ask_confirm is not None:
        given_failure.ask_confirm = ask_confirm
    if restricted_to_group_id is not None:
        given_failure.restricted_to_group_id = restricted_to_group_id

    return given_failure


def failure_add(failure_id: FailureId, child_failure_id: FailureId) -> None:
    """
    Adds a new child to an existing failure.
    :param failure_id: The ID of the failure to add the child to.
    :param child_failure_id: The ID of the child failure.
    """
    Failure.get(failure_id).add_child(Failure.get(child_failure_id))
