from typing import Optional, TypeAlias

from qrbug.tree import Tree
from qrbug.failure import FailureId

ThingId: TypeAlias = str


class Thing(Tree):
    """
    A Thing that can fail.
    """
    instances: dict[ThingId, "Thing"] = {}

    # Default values
    location:   Optional[str]       = None
    failure_id: Optional[FailureId] = None
    comment:    Optional[str]       = ""

    def _local_dump(self) -> str:
        return f"Thing(id={self.id}, location={self.location}, comment={self.comment})"


def thing_update(thing_id: ThingId, **kwargs) -> Thing:
    """
    Creates a new thing that can fail, or modifies an existing one.
    :param thing_id: The ID of this thing.
    :param location: Where this thing is located.
    :param failure_id: Which is the root failure for this thing ?
    :param comment: Any comment on the thing.
    """
    return Thing.update_attributes(thing_id, **kwargs)


def thing_del(thing_id: ThingId) -> None:
    """
    Deletes an existing thing.
    :param thing_id: The ID of this thing.
    """
    del Thing.instances[thing_id]
