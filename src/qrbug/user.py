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

qrbug.User = User
qrbug.UserId = UserId
qrbug.user_update = User.update_attributes
qrbug.user_add = User.add_parenting_link
qrbug.user_remove = User.remove_parenting_link

if __name__ == "__main__":
    user_add("0", "1")
    print(User["0"].dump())
