"""
Defines a user of the app.
"""
from typing import TypeAlias

from qrbug.tree import Tree

UserId: TypeAlias = str


class User(Tree):
    """
    A user of the app.
    """
    instances: dict[UserId, "User"] = {}

    def __init__(self, user: UserId):
        """
        Creates a new user.
        :param user: The ID of this new user.
        """
        self._init(user)

    # def _local_dump(self) -> str:
    #     return "User()"


def user_add(parent: UserId, child: UserId) -> None:
    """
    Sets a new user to be the child of another user.
    :param parent: The ID of the user to parent the new child to.
    :param child: The ID of the child to add to the parent.
    """
    User.add_parenting_link(parent, child)


def user_remove(parent: UserId, child: UserId) -> None:
    """
    Removes the parenting link from a user to another.
    :param parent: The ID of the user to remove the child from.
    :param child: The ID of the user to be removed.
    """
    User.remove_parenting_link(parent, child)
