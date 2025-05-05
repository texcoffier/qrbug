"""
Defines a user of the app.
"""
from typing import TypeAlias

UserId: TypeAlias = str


class User:
    """
    A user of the app.
    """
    instances: dict[UserId, "User"] = {}  # Maps every user ID to a user instance

    def __init__(self, user: UserId):
        """
        Creates a new user.
        :param user: The ID of this new user.
        """
        self.user_id: UserId = user
        self.children_ids: list[UserId] = []

    def user_add(self, child: "User") -> None:
        """
        Adds a new child to this user's children.
        :param child: Another user.
        """
        assert child.user_id not in self.children_ids, f"{child.user_id} is already a child of {self.user_id}"
        assert child.user_id != self.user_id, f"Cannot make {child.user_id} a child of itself !"
        self.children_ids.append(child.user_id)

    @classmethod
    def get(cls, user: UserId) -> "User":
        """
        Returns the user at the given ID.
        **Warning :** If the user doesn't exist, a brand new one is created.
        :param user: The ID of this user.
        :return: The user at the given ID.
        """
        if user not in User.instances:
            User.instances[user] = User(user)
        return User.instances[user]

    def dump(self) -> str:
        """
        Gives a printable representation of this user.
        :return: A printable representation of this user.
        """
        return f"{self.user_id} {self.children_ids}"


def user_add(parent: UserId, child: UserId) -> None:
    """
    Sets a new user to be the child of another user.
    :param parent: The ID of the user to parent the new child to.
    :param child: The ID of the child to add to the parent.
    """
    User.get(parent).user_add(User.get(child))
