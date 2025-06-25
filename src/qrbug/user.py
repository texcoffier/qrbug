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

    def rename_to(self, new_user_id: str):
        if new_user_id in self.instances.keys():
            raise IndexError('User ID already exists')

        old_id = self.id
        self.id = new_user_id
        self.instances[new_user_id] = self
        del self.instances[old_id]

        # Rename in children and in parents of all instances
        for instance in self.instances.values():
            if old_id in instance.children_ids:
                instance.children_ids.remove(old_id)
                instance.children_ids.append(new_user_id)
            if old_id in instance.parent_ids:
                instance.parent_ids.remove(old_id)
                instance.parent_ids.add(new_user_id)

        # Rename in "users" of Concerned
        for instance in qrbug.Failure.instances.values():
            if instance.allowed == old_id:
                instance.allowed = new_user_id

        # Rename in "users" of Concerned
        for instance in qrbug.Concerned.instances.values():
            if old_id in instance.users:
                instance.users.remove(old_id)
                instance.users.add(new_user_id)


def user_rename(old_user_id: UserId, new_user_id: UserId):
    old_user = User[old_user_id]
    if old_user is None:
        raise Exception('User ID does not exist')
    old_user.rename_to(new_user_id)

qrbug.User = User
qrbug.UserId = UserId
qrbug.user_update = User.update_attributes
qrbug.user_add = User.add_parenting_link
qrbug.user_remove = User.remove_parenting_link
qrbug.user_rename = user_rename

if __name__ == "__main__":
    user_add("0", "1")
    print(User["0"].dump())
