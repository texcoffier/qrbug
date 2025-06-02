import sys
import unittest
from pathlib import Path

import qrbug.init
import qrbug

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
    "Incident": qrbug.Incident,
    "exec_code_file": qrbug.exec_code_file,
    "CONFIGS": qrbug.CONFIGS,
    "INCIDENT_FUNCTIONS": qrbug.INCIDENT_FUNCTIONS,
    "TestCase": qrbug.TestCase,
}

qrbug.SETTINGS = SETTINGS
qrbug.QRBUG = QRBUG
