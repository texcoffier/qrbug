import sys
import unittest
from pathlib import Path

import qrbug.init
import qrbug

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

SETTINGS = {
    "TOKEN_LOGIN_TIMEOUT": qrbug.TOKEN_LOGIN_TIMEOUT,
    "CAS_URL": qrbug.CAS_URL,
    "SERVICE_URL": qrbug.SERVICE_URL,
    "JOURNALS_FILE_PATH": qrbug.JOURNALS_FILE_PATH,
    "DB_FILE_PATH": qrbug.DB_FILE_PATH,
    "INCIDENTS_FILE_PATH": qrbug.INCIDENTS_FILE_PATH,
    "DEFAULT_DB_PATH": qrbug.DEFAULT_DB_PATH,
}

QRBUG = {
    **qrbug.CONFIGS,
    **qrbug.INCIDENT_FUNCTIONS,
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
