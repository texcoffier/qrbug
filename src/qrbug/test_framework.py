import unittest
import sys
from pathlib import Path

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
        qrbug.exec_code_file(Path(test.replace('.py', '_db.conf')), qrbug.CONFIGS)


qrbug.TestCase = TestCase
