import unittest
import sys
from pathlib import Path

import qrbug

async def nothing(x):
    return f'{x}@?'

class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        qrbug.Request = qrbug.FakeRequest
        qrbug.INCIDENTS_FILE_PATH = Path("TESTS", "xxx-incidents.py")
        qrbug.DB_FILE_PATH = Path("TESTS", "xxx-db.py")
        if qrbug.DB_FILE_PATH.exists():
            qrbug.DB_FILE_PATH.unlink()
        qrbug.get_mail_from_login = nothing


    def tearDown(self):
        qrbug.User.instances.clear()
        qrbug.Failure.instances.clear()
        qrbug.Thing.instances.clear()
        qrbug.Incident.instances.clear()
        qrbug.Incident.pending_feedback = {}

    def check(self, cls, value):
        # The parameters are arranged in this order because the EXPECTED value goes first, followed by the
        # actual value of the class dump
        self.assertEqual(value, '\n'.join(sorted(cls.dump_all())))

    def load_config(self):
        test = sys.modules[self.__class__.__module__].__spec__.origin
        qrbug.exec_code_file(Path(test.replace('.py', '_db.conf')), qrbug.CONFIGS)


class File:
    def __init__(self, lines):
        self.lines = lines
    async def write(self, data):
        self.lines.append(data)
class FakeRequest:
    report = None
    def __init__(self, incident=None, create_secret=True):
        self.lines = []
        self.response = File(self.lines)
        if incident:
            self.report = incident.active[-1]
        self.write = self.response.write
        if not incident:
            class FakeIncident:
                thing_id = 'Fake Thing ID'
                failure_id = 'Fake Failure ID'
            incident = FakeIncident
        self.incident = incident
        if create_secret:
            self.secret = qrbug.update_secret('unittest_secret')
    @staticmethod
    def update_configuration(line):
        qrbug.append_line_to_journal(line, qrbug.Journals.DB)

qrbug.TestCase = TestCase
qrbug.FakeRequest = FakeRequest