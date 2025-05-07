import unittest
from pathlib import Path

from qrbug.user import User, user_remove, user_add
from qrbug.journals import exec_code_file


class TestUser(unittest.TestCase):
    def setUp(self):
        User.instances.clear()

    def tearDown(self):
        User.instances.clear()

    def test_creation(self):
        # Tests whether adding two users grows the instances count accordingly
        self.assertEqual(len(User.instances), 0)
        user_add("0", "1")
        self.assertEqual(len(User.instances), 2)

        # Tests whether both IDs are in the list of instances
        self.assertEqual(sorted(User.instances), ['0', '1'])

        # Tests the amount of children
        self.assertEqual(len(User.instances["0"].children_ids), 1)
        self.assertEqual(len(User.instances["1"].children_ids), 0)

        # Tests that 0 has 1 as child
        self.assertEqual(User.instances["0"].children_ids, {"1"})

    def test_deletion(self):
        # Test setup, adding the children (instead of using user_add())
        User.instances = {
            "0": User("0"),
            "1": User("1"),
        }
        User.instances["0"].children_ids = {"1"}

        # Tests that after deleting the link from 0 to 1, 0 is no longer the parent of 1
        user_remove("0", "1")
        self.assertEqual(len(User.instances["0"].children_ids), 0)

    def test_with_db(self):
        # Loads the DB where two users are created
        exec_code_file(str(Path(__file__).with_suffix('')) + "_db.conf", {
            "user_add": user_add,
            "user_remove": user_remove,
        })

        # Checks that there are two users in the DB
        self.assertEqual(len(User.instances), 2)
