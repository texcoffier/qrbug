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

    def _local_dump(self) -> str:
        return self.get_representation()


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

if __name__ == "__main__":
    user_add("0", "1")
    print(User.get("0").dump())
