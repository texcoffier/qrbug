"""
Defines a user of the app.
"""
from typing import TypeAlias

UserId: TypeAlias = str


class User:
	instances: dict[UserId, "User"] = {}

	def __init__(self, user: UserId):
		self.user_id = user
		self.children_ids = []

	def user_add(self, child: "User") -> None:
		assert child.user_id not in self.children_ids
		self.children_ids.append(child.user_id)

	@classmethod
	def get(cls, user: UserId) -> "User":
		if user not in User.instances:
			User.instances[user] = User(user)
		return User.instances[user]

	def dump(self) -> str:
		return f"{self.user_id} {self.children_ids}"


def user_add(parent: UserId, child: UserId) -> None:
	User.get(parent).user_add(User.get(child))
