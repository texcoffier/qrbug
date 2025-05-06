import unittest
from qrbug.failure import Failure, failure_update, failure_add, failure_remove


class TestFailure(unittest.TestCase):
    creation_test_passed = False
    parenting_test_passed = False

    def setUp(self):
        Failure.instances.clear()

    def tearDown(self):
        Failure.instances.clear()

    def test_creation(self):
        # Checks that the failures are actually registered upon creation
        self.assertEqual(len(Failure.instances), 0)
        failure: Failure = failure_update("0")  # Creates a brand-new failure with ID zero
        self.assertEqual(len(Failure.instances), 1)  # Checks that the failure actually got registered

        # Checks that the new failure has the correct ID and no children
        self.assertEqual(failure.failure_id, "0")
        self.assertEqual(len(failure.children_ids), 0)

        # Checks that updating an attribute of the failure class works
        new_value = "There is a new value"
        old_value = failure.value
        failure_update("0", value=new_value)
        self.assertEqual(failure.value, new_value)
        self.assertNotEqual(old_value, failure.value)

        # Checks that updating a non-existent attribute of the failure class DOESN'T work
        self.assertRaises(AssertionError, failure_update, "0", non_existent_key="value")

        # Checks that updating the instances dictionary of the failure class DOESN'T work
        self.assertRaises(AssertionError, failure_update, "0", instances={})

        # Makes sure the other tests know that the creation of failures works
        TestFailure.creation_test_passed = True

    def test_parenting(self):
        if TestFailure.creation_test_passed is False:
            raise unittest.SkipTest(
                "Creation test did not succeed, parenting test cannot work without creation test passing"
            )

        self.assertEqual(len(Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures
        a = failure_update("0")
        b = failure_update("1")

        # Checks that those two failures have no children
        for failure in (a, b):
            self.assertEqual(len(failure.children_ids), 0)

        # Parents 0 to 1 (adds 1 as the child of 0)
        failure_add(a.failure_id, b.failure_id)
        self.assertEqual(len(a.children_ids), 1)
        self.assertEqual(len(b.children_ids), 0)
        self.assertEqual(a.children_ids[0], b.failure_id)

        TestFailure.parenting_test_passed = True

    def test_unparenting(self):
        if TestFailure.creation_test_passed is False:
            raise unittest.SkipTest(
                "Creation test did not succeed, unparenting test cannot work without creation test passing"
            )
        if TestFailure.parenting_test_passed is False:
            raise unittest.SkipTest(
                "Parenting test did not succeed, unparenting test cannot work without parenting test passing"
            )

        self.assertEqual(len(Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures and parents them
        a = failure_update("0")
        b = failure_update("1")
        failure_add(a.failure_id, b.failure_id)

        # Tests that both failures, if unparented, have no children anymore
        failure_remove(a.failure_id, b.failure_id)
        for failure in (a, b):
            self.assertEqual(len(failure.children_ids), 0)
