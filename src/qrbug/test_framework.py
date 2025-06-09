import unittest
import sys
from pathlib import Path

import qrbug

class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        qrbug.INCIDENTS_FILE_PATH = Path("TESTS", "xxx-incidents.py")
        qrbug.DB_FILE_PATH = Path("TESTS", "xxx-db.py")
        if qrbug.DB_FILE_PATH.exists():
            qrbug.DB_FILE_PATH.unlink()


    def tearDown(self):
        qrbug.User.instances.clear()
        qrbug.Failure.instances.clear()
        qrbug.Thing.instances.clear()
        qrbug.Incident.instances.clear()
        qrbug.Concerned.instances.clear()

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
        self.lines.append(data.decode('utf-8'))
class Request:
    def __init__(self):
        self.lines = []
        self.response = File(self.lines)

qrbug.TestCase = TestCase
qrbug.Request = Request
