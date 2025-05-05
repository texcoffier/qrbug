"""
Defines all kinds of failures that can happen on a thing.
"""
from typing import Optional, TypeAlias

FailureId: TypeAlias = str


class Failure:
    instances: dict[FailureId, "Failure"] = {}

    def __init__(self, failure_id: FailureId, title: Optional[str], display: Optional[str],
                 ask_confirm: Optional[bool] = None, restricted_to_group_id: Optional[str] = None):
        self.failure_id = failure_id
        self.title = title
        self.display = display
        self.ask_confirm = ask_confirm
        self.restricted_to_group_id = restricted_to_group_id
        self.child_failures: list[FailureId] = []

    def add_child(self, child: "Failure"):
        assert child.failure_id not in self.child_failures, f"{child.failure_id} is already a child of {self.failure_id}"
        assert child.failure_id != self.failure_id, f"Cannot make {child.failure_id} a child of itself !"
        self.child_failures.append(child.failure_id)

    @classmethod
    def get(cls, failure: FailureId) -> "Failure":
        if failure not in Failure.instances:
            Failure.instances[failure] = Failure(failure)
        return Failure.instances[failure]


def failure_add(failure_id: FailureId, child_failure_id: FailureId):
    Failure.get(failure_id).add_child(Failure.get(child_failure_id))
