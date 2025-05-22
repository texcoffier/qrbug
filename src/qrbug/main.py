import sys
import unittest
from pathlib import Path

import qrbug.init
import qrbug


def set_db_path(path: Path) -> None:
    global DB_FILE_PATH
    DB_FILE_PATH = path


def set_incidents_path(path: Path) -> None:
    global INCIDENTS_FILE_PATH
    INCIDENTS_FILE_PATH = path


def dispatch(
        dispatch_id: qrbug.DispatcherId,
        failure_ids: list[qrbug.FailureId],
        action_id: qrbug.ActionId,
        group_id: qrbug.UserId,
        timestamp: int
) -> None:
    dispatcher = qrbug.Dispatcher[dispatch_id]
    if dispatcher is None:
        return

    # Looks for every incident with the given failure ids
    dispatched_incidents = []
    for failure_id in failure_ids:
        for current_incident in qrbug.Incidents.filter_active(failure_id=failure_id):
            dispatched_incidents.append(current_incident)

    dispatcher.run(dispatched_incidents, group_id, None)

class TestCase(unittest.TestCase):
    def tearDown(self):
        qrbug.User.instances.clear()
        qrbug.Failure.instances.clear()

    def check(self, cls, value):
        # The parameters are arranged in this order because the EXPECTED value goes first, followed by the
        # actual value of the class dump
        self.assertEqual(value, '\n'.join(sorted(cls.dump_all())))

    def load_config(self):
        test = sys.modules[self.__class__.__module__].__spec__.origin
        qrbug.exec_code_file(Path(test.replace('.py', '_db.conf')), CONFIGS)


qrbug.TestCase = TestCase
qrbug.dispatch = dispatch
qrbug.set_db_path = set_db_path
qrbug.set_incidents_path = set_incidents_path

INCIDENT_FUNCTIONS = {
    "incident": qrbug.incident,
    "incident_del": qrbug.incident_del,
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
    "User": qrbug.User,
    "Failure": qrbug.Failure,
    "Thing": qrbug.Thing,
    "Action": qrbug.Action,
    "Selector": qrbug.Selector,
    "Dispatcher": qrbug.Dispatcher,
    "Incidents": qrbug.Incidents,
    "exec_code_file": qrbug.exec_code_file,
    "CONFIGS": qrbug.CONFIGS,
    "INCIDENT_FUNCTIONS": INCIDENT_FUNCTIONS,
    "TestCase": TestCase,
}

qrbug.INCIDENT_FUNCTIONS = INCIDENT_FUNCTIONS
qrbug.SETTINGS = SETTINGS
qrbug.QRBUG = QRBUG
