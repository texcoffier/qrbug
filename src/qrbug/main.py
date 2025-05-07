import os
from typing import Optional, Callable
from dataclasses import dataclass

from qrbug.user import user_add, user_remove, UserId
from qrbug.failure import failure_update, failure_add, failure_remove, DisplayTypes, FailureId
from qrbug.thing import thing_update, thing_del, ThingId
from qrbug.action import action, ActionId
from qrbug.selector import selector
from qrbug.dispatcher import dispatcher_update, dispatcher_del, DispatcherId

# Journal files
JOURNALS_FILE_PATH = "JOURNALS/"
DB_FILE_PATH = os.path.join(JOURNALS_FILE_PATH, "db.py")
FAILURES_FILE_PATH = os.path.join(JOURNALS_FILE_PATH, "failures.py")

# Failures remaining
@dataclass
class CurrentFailure:
    thing_id: ThingId
    failure_id: FailureId
    ip: str
    timestamp: int
    comment: Optional[str] = None

CURRENT_FAILURES: list[CurrentFailure] = []


def failure(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int, comment: Optional[str] = None) -> None:
    CURRENT_FAILURES.append(CurrentFailure(thing_id, failure_id, ip, timestamp, comment))


def failure_del(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int) -> None:
    for current_failure in CURRENT_FAILURES:
        if current_failure.thing_id == thing_id and current_failure.failure_id == failure_id:
            CURRENT_FAILURES.remove(current_failure)
            break


def dispatch(
        dispatch_id: DispatcherId,
        failure_ids: list[FailureId],
        action_id: ActionId,
        group_id: UserId,
        timestamp: int
) -> None:
    pass


def exec_code_file(path: str, code_globals: dict[str, Callable]) -> None:
    with open(path, 'r', encoding='utf-8') as f:
        file_contents = f.read()
    file_code = compile(file_contents, path, 'exec')
    exec(file_code, code_globals)


def load_config() -> None:
    exec_code_file(DB_FILE_PATH, {
        "user_add": user_add,
        "user_remove": user_remove,
        "failure_update": failure_update,
        "failure_add": failure_add,
        "failure_remove": failure_remove,
        "DisplayTypes": DisplayTypes,
        "thing_update": thing_update,
        "thing_del": thing_del,
        "action": action,
        "selector": selector,
        "dispatcher_update": dispatcher_update,
        "dispatcher_del": dispatcher_del,
    })


def load_failures() -> None:
    exec_code_file(FAILURES_FILE_PATH, {
        "failure": failure,
        "failure_del": failure_del,
        "dispatch": dispatch,
    })


if __name__ == "__main__":
    from qrbug.failure import Failure
    from qrbug.user import User

    print(Failure.instances)
    print(User.instances)
    load_config()
    print(Failure.instances)
    print(User.instances)
