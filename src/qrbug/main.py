import sys
import unittest
from pathlib import Path

from qrbug.action import action, ActionId, Action
from qrbug.dispatcher import dispatcher_update, dispatcher_del, DispatcherId, Dispatcher
from qrbug.failure import failure_update, failure_add, failure_remove, DisplayTypes, FailureId, Failure
from qrbug.incidents import incident, incident_del, Incidents
from qrbug.selector import selector, Selector
from qrbug.thing import thing_update, thing_del, Thing
from qrbug.user import user_add, user_remove, UserId, User

from qrbug.journals import exec_code_file, DB_FILE_PATH, INCIDENTS_FILE_PATH


def dispatch(
        dispatch_id: DispatcherId,
        failure_ids: list[FailureId],
        action_id: ActionId,
        group_id: UserId,
        timestamp: int
) -> None:
    dispatcher = Dispatcher[dispatch_id]
    if dispatcher is None:
        return

    dispatcher.run(failure_ids)


CONFIGS = {
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
    }


class TestCase(unittest.TestCase):
    def tearDown(self):
        User.instances.clear()
        Failure.instances.clear()

    def check(self, cls, value):
        # The parameters are arranged in this order because the EXPECTED value goes first, followed by the
        # actual value of the class dump
        self.assertEqual(value, '\n'.join(sorted(cls.dump_all())))

    def load_config(self):
        test = sys.modules[self.__class__.__module__].__spec__.origin
        exec_code_file(Path(test.replace('.py', '_db.conf')), CONFIGS)

