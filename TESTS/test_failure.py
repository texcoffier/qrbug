import qrbug.init
import qrbug


class TestFailure(qrbug.TestCase):
    def test_creation(self):
        # Checks that the failures are actually registered upon creation
        self.check(qrbug.Failure, '')
        qrbug.failure_update('0')  # Creates a brand-new failure with ID zero
        self.check(qrbug.Failure, f'0 [] val:\'VALEUR_NON_DEFINIE POUR «0»\' type:text confirm:')

        # Checks that updating an attribute of the failure class works
        new_value = 'There is a new value'
        qrbug.failure_update('0', value=new_value)
        self.check(qrbug.Failure, f"0 [] val:'{new_value}' type:text confirm:")

        # Checks that updating a non-existent attribute of the failure class DOESN'T work
        # self.assertRaises(AssertionError, qrbug.failure_update, '0', non_existent_key='value')

        # Checks that updating the instances dictionary of the failure class DOESN'T work
        # self.assertRaises(AssertionError, qrbug.failure_update, '0', instances={})

    def test_parenting(self):
        self.assertEqual(len(qrbug.Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures (instead of using failure_update())
        qrbug.failure_update('0')
        qrbug.failure_update('1')
        a = qrbug.Failure['0']
        b = qrbug.Failure['1']

        # Checks that those two failures have no children
        self.check(qrbug.Failure, f'0 [] val:\'VALEUR_NON_DEFINIE POUR «0»\' type:text confirm:\n'
                            f'1 [] val:\'VALEUR_NON_DEFINIE POUR «1»\' type:text confirm:')

        # Parents 0 to 1 (adds 1 as the child of 0)
        qrbug.failure_add(a.id, b.id)
        self.check(qrbug.Failure, f"0 ['1'] val:\'VALEUR_NON_DEFINIE POUR «0»\' type:text confirm:\n"
                            f'1 [] val:\'VALEUR_NON_DEFINIE POUR «1»\' type:text confirm:')

    def test_unparenting(self):
        self.assertEqual(len(qrbug.Failure.instances), 0)  # Checks that there are no failures created yet

        # Creates two failures and parents them (instead of using failure_update() and failure_add())
        qrbug.failure_update('0')
        qrbug.failure_update('1')
        a = qrbug.Failure['0']
        b = qrbug.Failure['1']
        qrbug.failure_add(a.id, b.id)

        # Tests that both failures, if unparented, have no children anymore
        qrbug.failure_remove(a.id, b.id)
        self.check(qrbug.Failure, f'0 [] val:\'VALEUR_NON_DEFINIE POUR «0»\' type:text confirm:\n'
                            f'1 [] val:\'VALEUR_NON_DEFINIE POUR «1»\' type:text confirm:')

    def test_with_db(self):
        # Loads the DB where a simple failure is created
        self.load_config()
        # Checks that there are two users in the DB
        self.check(qrbug.Failure, f"PC_NO_BOOT [] val:'Le PC ne démarre pas' type:text confirm:")

    def test_move_failure(self):
        qrbug.failure_update('parent')
        qrbug.failure_update('child1')
        qrbug.failure_update('child2')
        qrbug.failure_add('parent', 'child1')
        qrbug.failure_add('parent', 'child2')
        self.assertEqual(qrbug.Failure['parent'].children_ids, ['child1', 'child2'])
        qrbug.failure_move('parent', 'child2', 'child1')
        self.assertEqual(qrbug.Failure['parent'].children_ids, ['child2', 'child1'])
