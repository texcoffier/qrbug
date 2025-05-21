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
from qrbug.journals import exec_code_file


# SETTINGS
TOKEN_LOGIN_TIMEOUT = 60
CAS_URL = 'https://cas.univ-lyon1.fr/cas'
SERVICE_URL = 'http://qrbug.univ-lyon1.fr:8080/'

# Journal files
JOURNALS_FILE_PATH = Path("JOURNALS")
DB_FILE_PATH = JOURNALS_FILE_PATH / "db.py"
DEFAULT_DB_PATH = JOURNALS_FILE_PATH / "default_db.py"
INCIDENTS_FILE_PATH = JOURNALS_FILE_PATH / "incidents.py"


def set_db_path(path: Path) -> None:
    global DB_FILE_PATH
    DB_FILE_PATH = path


def set_incidents_path(path: Path) -> None:
    global INCIDENTS_FILE_PATH
    INCIDENTS_FILE_PATH = path


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

    # Looks for every incident with the given failure ids
    dispatched_incidents = [
        current_incident
        for current_incident in Incidents.active
        if current_incident.failure_id in failure_ids
    ]

    dispatcher.run(dispatched_incidents, group_id, None)

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

INCIDENT_FUNCTIONS = {
    "incident": incident,
    "incident_del": incident_del,
    "dispatch": dispatch,
}

SETTINGS = {
    "TOKEN_LOGIN_TIMEOUT": TOKEN_LOGIN_TIMEOUT,
    "CAS_URL": CAS_URL,
    "SERVICE_URL": SERVICE_URL,
    "JOURNALS_FILE_PATH": JOURNALS_FILE_PATH,
    "DB_FILE_PATH": DB_FILE_PATH,
    "INCIDENTS_FILE_PATH": INCIDENTS_FILE_PATH,
    "DEFAULT_DB_PATH": DEFAULT_DB_PATH,
}

QRBUG = {
    **CONFIGS,
    **INCIDENT_FUNCTIONS,
    **SETTINGS,
    "User": User,
    "Failure": Failure,
    "Thing": Thing,
    "Action": Action,
    "Selector": Selector,
    "Dispatcher": Dispatcher,
    "Incidents": Incidents,
    "exec_code_file": exec_code_file,
    "CONFIGS": CONFIGS,
    "INCIDENT_FUNCTIONS": INCIDENT_FUNCTIONS,
    "TestCase": TestCase,
}
