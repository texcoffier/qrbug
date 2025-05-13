import qrbug.main as qrbug_main


class TestFailure(qrbug_main.TestCase):
    def test_creation(self):
        # Checks that the failures are actually registered upon creation
        self.check(qrbug_main.Failure, '')
        qrbug_main.failure_update('0')  # Creates a brand-new failure with ID zero
        self.check(qrbug_main.Failure, f'0 [] {qrbug_main.Failure.__name__}()')

        # Checks that updating an attribute of the failure class works
        new_value = 'There is a new value'
        qrbug_main.failure_update('0', value=new_value)
        self.check(qrbug_main.Failure, f"0 [] {qrbug_main.Failure.__name__}(value='{new_value}')")

        # Checks that updating a non-existent attribute of the failure class DOESN'T work
        self.assertRaises(AssertionError, qrbug_main.failure_update, '0', non_existent_key='value')

        # Checks that updating the instances dictionary of the failure class DOESN'T work
        self.assertRaises(AssertionError, qrbug_main.failure_update, '0', instances={})

    def test_parenting(self):
        self.assertEqual(len(qrbug_main.Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures (instead of using failure_update())
        a = qrbug_main.Failure.get('0')
        b = qrbug_main.Failure.get('1')

        # Checks that those two failures have no children
        self.check(qrbug_main.Failure, f'0 [] {qrbug_main.Failure.__name__}()\n'
                            f'1 [] {qrbug_main.Failure.__name__}()')

        # Parents 0 to 1 (adds 1 as the child of 0)
        qrbug_main.failure_add(a.id, b.id)
        self.check(qrbug_main.Failure, f"0 ['1'] {qrbug_main.Failure.__name__}()\n"
                            f'1 [] {qrbug_main.Failure.__name__}()')

    def test_unparenting(self):
        self.assertEqual(len(qrbug_main.Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures and parents them (instead of using failure_update() and failure_add())
        a = qrbug_main.Failure.get('0')
        b = qrbug_main.Failure.get('1')
        qrbug_main.failure_add(a.id, b.id)

        # Tests that both failures, if unparented, have no children anymore
        qrbug_main.failure_remove(a.id, b.id)
        self.check(qrbug_main.Failure, f'0 [] {qrbug_main.Failure.__name__}()\n'
                            f'1 [] {qrbug_main.Failure.__name__}()')

    def test_with_db(self):
        # Loads the DB where a simple failure is created
        self.load_config()
        # Checks that there are two users in the DB
        self.check(qrbug_main.Failure, f"PC_NO_BOOT [] {qrbug_main.Failure.__name__}(ask_confirm=False, restricted_to_group_id='ROOT', value='Le PC ne démarre pas')")
