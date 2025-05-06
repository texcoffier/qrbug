"""
Defines all kinds of failures that can happen on a thing.
"""
from typing import Optional, TypeAlias

from qrbug.tree import Tree
from qrbug.failure import FailureId

ThingId: TypeAlias = str


class Thing(Tree):
    """
    A Thing that can fail.
    """
    # Default values
    location:   Optional[str]       = None
    failure_id: Optional[FailureId] = None
    comment:    Optional[str]       = ""


    def __init__(self, thing_id: ThingId):
        """
        Creates a new thing that can fail.
        :param thing_id: The ID of this thing.
        """
        super().__init__(thing_id)


def thing_update(thing_id: ThingId, **kwargs) -> Thing:
    """
    Creates a new thing that can fail, or modifies an existing one.
    :param thing_id: The ID of this thing.
    :param location: Where this thing is located.
    :param failure_id: Which is the root failure for this thing ?
    :param comment: Any comment on the thing.
    """
    # Gets the thing the user asked for (or creates one with the corresponding ID if it did not exist)
    thing = Thing.get(thing_id)

    # Sets the new data of the thing
    for arg, value in kwargs.items():
        assert hasattr(Thing, arg), f"Class {Thing.__class__.__name__} has no attribute '{arg}', do not attempt to update it"
        assert arg != "instances", f"Cannot update instances of {Thing.__class__.__name__} class, please do not attempt"
        setattr(thing, arg, value)

    return thing


def thing_del(thing_id: ThingId) -> None:
    """
    Deletes an existing thing.
    :param thing_id: The ID of this thing.
    """
    del Thing.instances[thing_id]
