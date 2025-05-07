import os
from typing import Optional

from qrbug.user import user_add, user_remove, UserId
from qrbug.failure import failure_update, failure_add, failure_remove, DisplayTypes, FailureId
from qrbug.thing import thing_update, thing_del, ThingId
from qrbug.action import action, ActionId
from qrbug.selector import selector
from qrbug.dispatcher import dispatcher_update, dispatcher_del, DispatcherId


JOURNALS_FILE_PATH = "JOURNALS/"
DB_FILE_PATH = os.path.join(JOURNALS_FILE_PATH, "db.py")
FAILURES_FILE_PATH = os.path.join(JOURNALS_FILE_PATH, "failures.py")


def failure(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int, comment: Optional[str]) -> None:
    pass


def failure_del(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int) -> None:
    pass

def dispatch(
    dispatch_id: DispatcherId,
    failure_ids: list[FailureId],
    action_id: ActionId,
    group_id: UserId,
    timestamp: int
) -> None:
    pass


def load_config() -> None:
    with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
        db_file_contents = f.read()
    db_file_code = compile(db_file_contents, DB_FILE_PATH, 'exec')
    exec(db_file_code, {
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
    with open(FAILURES_FILE_PATH, 'r', encoding='utf-8') as f:
        failures_file_contents = f.read()
    failures_file_code = compile(failures_file_contents, FAILURES_FILE_PATH, 'exec')
    exec(failures_file_code, {
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
