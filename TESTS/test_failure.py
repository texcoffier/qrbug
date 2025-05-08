from qrbug.main import *
class TestFailure(TestCase):
    def test_creation(self):
        # Checks that the failures are actually registered upon creation
        self.check(Failure,
                   "")
        failure: Failure = failure_update("0")  # Creates a brand-new failure with ID zero
        self.check(Failure,
                   "0 [] Failure(value=VALEUR_NON_DEFINIE, display_type=DisplayTypes.text, ask_confirm=True, restricted_to_group_id=None)")

        # Checks that the new failure has the correct ID and no children
        self.assertEqual(failure.id, "0")
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

    def test_parenting(self):
        self.assertEqual(len(Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures (instead of using failure_update())
        a = Failure("0")
        b = Failure("1")
        for failure in (a, b):
            Failure.instances[failure.id] = failure

        # Checks that those two failures have no children
        for failure in (a, b):
            self.assertEqual(len(failure.children_ids), 0)

        # Parents 0 to 1 (adds 1 as the child of 0)
        failure_add(a.id, b.id)
        self.assertEqual(len(a.children_ids), 1)
        self.assertEqual(len(b.children_ids), 0)
        self.assertEqual(a.children_ids, {b.id})

    def test_unparenting(self):
        self.assertEqual(len(Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures and parents them (instead of using failure_update() and failure_add())
        a = Failure("0")
        b = Failure("1")
        a.children_ids = {"1"}
        for failure in (a, b):
            Failure.instances[failure.id] = failure

        # Tests that both failures, if unparented, have no children anymore
        failure_remove(a.id, b.id)
        for failure in (a, b):
            self.assertEqual(len(failure.children_ids), 0)

    def test_with_db(self):
        # Loads the DB where a simple failure is created
        self.load_config()
        # Checks that there are two users in the DB
        self.assertEqual(len(Failure.instances), 1)
        self.assertIn("PC_NO_BOOT", Failure.instances)
