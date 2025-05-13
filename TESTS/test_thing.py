import qrbug

ID = '0'


class TestThing(qrbug.main.TestCase):
    def test_creation(self):
        self.check(qrbug.main.Thing, '')
        qrbug.main.thing_update(ID)
        self.check(qrbug.main.Thing, f'{ID} [] ()')

    def test_update(self):
        # Creates a thing (without using the thing_update()) method
        qrbug.main.Thing.get(ID)

        # Updates said thing
        new_value = 'THIS IS A NEW VALUE FOR THE COMMENT'
        qrbug.main.thing_update(ID, comment=new_value)
        self.check(qrbug.main.Thing, f"{ID} [] (comment='{new_value}')")

    def test_delete(self):
        # Creates a thing (without using the thing_update()) method
        qrbug.main.Thing.get(ID)

        # Tests around deleting an instance
        self.check(qrbug.main.Thing, f'{ID} [] ()')
        qrbug.main.thing_del(ID)
        self.check(qrbug.main.Thing, '')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug.main.Thing, f"0 [] (comment='A comment, it seems')")
