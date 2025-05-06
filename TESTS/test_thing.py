import unittest
from qrbug.thing import Thing, thing_update, thing_del


class TestThing(unittest.TestCase):
    def setUp(self):
        Thing.instances.clear()

    def tearDown(self):
        Thing.instances.clear()

    def test_creation(self):
        ID = "0"
        self.assertEqual(Thing.instances, {})
        thing_update(ID)
        self.assertEqual(sorted(list(Thing.instances.keys())), [ID])

    def test_update(self):
        ID = "0"
        # Creates a thing (without using the thing_update()) method
        a = Thing(ID)
        Thing.instances[ID] = a

        # Updates said thing
        old_value = a.comment
        new_value = "THIS IS A NEW VALUE FOR THE COMMENT"
        thing_update(ID, comment=new_value)
        self.assertNotEqual(old_value, new_value)
        self.assertNotEqual(old_value, a.comment)

    def test_delete(self):
        ID = "0"
        # Creates a thing (without using the thing_update()) method
        Thing.instances[ID] = Thing(ID)

        # Tests around deleting an instance
        self.assertEqual(len(Thing.instances), 1)
        thing_del(ID)
        self.assertEqual(len(Thing.instances), 0)

