"""
Defines a user of the app.
"""
from typing import TypeAlias

import qrbug

UserId: TypeAlias = str


class User(qrbug.Tree):
    """
    A user of the app.
    """
    instances: dict[UserId, "User"] = {}

    def _local_dump(self) -> str:
        return '()'


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


qrbug.User = User
qrbug.UserId = UserId
qrbug.user_add = user_add
qrbug.user_remove = user_remove

if __name__ == "__main__":
    user_add("0", "1")
    print(User.get("0").dump())
