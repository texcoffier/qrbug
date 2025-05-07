import os
from typing import Optional

from qrbug.action import action, ActionId
from qrbug.dispatcher import dispatcher_update, dispatcher_del, DispatcherId
from qrbug.failure import failure_update, failure_add, failure_remove, DisplayTypes, FailureId
from qrbug.incidents import Incidents
from qrbug.selector import selector
from qrbug.thing import thing_update, thing_del, ThingId
from qrbug.user import user_add, user_remove, UserId

from qrbug.journals import exec_code_file, DB_FILE_PATH, FAILURES_FILE_PATH


def incident(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int, comment: Optional[str] = None) -> None:
    Incidents.create(thing_id, failure_id, ip, timestamp, comment)


def incident_del(thing_id: ThingId, failure_id: FailureId, ip: str, timestamp: int) -> None:
    Incidents.remove(thing_id, failure_id)


def dispatch(
        dispatch_id: DispatcherId,
        failure_ids: list[FailureId],
        action_id: ActionId,
        group_id: UserId,
        timestamp: int
) -> None:
    pass


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


def load_incidents() -> None:
    exec_code_file(FAILURES_FILE_PATH, {
        "incident": incident,
        "incident_del": incident_del,
        "dispatch": dispatch,
    })


if __name__ == "__main__":
    load_config()
    load_incidents()
