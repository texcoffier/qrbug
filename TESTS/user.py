import unittest
from qrbug.user import User, user_remove, user_add


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
        self.assertIn("0", User.instances)
        self.assertIn("1", User.instances)

        # Tests the amount of children
        self.assertEqual(len(User.instances["0"].children_ids), 1)
        self.assertEqual(len(User.instances["1"].children_ids), 0)

        # Tests that 0 has 1 as child
        self.assertEqual(User.instances["0"].children_ids[0], "1")

    def test_deletion(self):
        # Test setup, adding the children (instead of using user_add())
        User.instances = {
            "0": User("0"),
            "1": User("1"),
        }
        User.instances["0"].children_ids = ["1"]

        # Tests that after deleting the link from 0 to 1, 0 is no longer the parent of 1
        user_remove("0", "1")
        self.assertEqual(len(User.instances["0"].children_ids), 0)
