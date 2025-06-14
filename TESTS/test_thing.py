import qrbug.init
import qrbug

ID = '0'


class TestThing(qrbug.TestCase):
    def test_creation(self):
        self.check(qrbug.Thing, '')
        qrbug.thing_update(ID)
        self.check(qrbug.Thing, f'{ID} [] failures:[] comment:\'\'')

    def test_update(self):
        # Creates a thing (without using the thing_update()) method
        qrbug.Thing.get(ID)

        # Updates said thing
        new_value = 'THIS IS A NEW VALUE FOR THE COMMENT'
        qrbug.thing_update(ID, comment=new_value)
        self.check(qrbug.Thing, f"{ID} [] failures:[] comment:'{new_value}'")

    def test_delete(self):
        # Creates a thing (without using the thing_update()) method
        qrbug.Thing.get(ID)

        # Tests around deleting an instance
        self.check(qrbug.Thing, f'{ID} [] failures:[] comment:\'\'')
        qrbug.thing_del(ID)
        self.check(qrbug.Thing, '')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug.Thing, f"0 [] failures:[] comment:'A comment, it seems'")

    def test_add_failure(self):
        qrbug.Thing.get(ID)
        qrbug.thing_add_failure(ID, 'test-failure1')
        self.check(qrbug.Thing, "0 [] failures:['test-failure1'] comment:''")
        qrbug.thing_add_failure(ID, 'test-failure2')
        self.check(qrbug.Thing, "0 [] failures:['test-failure1', 'test-failure2'] comment:''")
        qrbug.thing_add_failure(ID, 'test-failure3')
        self.check(qrbug.Thing, "0 [] failures:['test-failure1', 'test-failure2', 'test-failure3'] comment:''")
        qrbug.thing_del_failure(ID, 'test-failure2')
        self.check(qrbug.Thing, "0 [] failures:['test-failure1', 'test-failure3'] comment:''")
        qrbug.thing_add_failure(ID, 'test-failure1')
        self.check(qrbug.Thing, "0 [] failures:['test-failure3', 'test-failure1'] comment:''")
