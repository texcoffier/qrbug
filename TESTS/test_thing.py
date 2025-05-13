import qrbug.main as qrbug_main

ID = '0'


class TestThing(qrbug_main.TestCase):
    def test_creation(self):
        self.check(qrbug_main.Thing, '')
        qrbug_main.thing_update(ID)
        self.check(qrbug_main.Thing, f'{ID} [] ()')

    def test_update(self):
        # Creates a thing (without using the thing_update()) method
        qrbug_main.Thing.get(ID)

        # Updates said thing
        new_value = 'THIS IS A NEW VALUE FOR THE COMMENT'
        qrbug_main.thing_update(ID, comment=new_value)
        self.check(qrbug_main.Thing, f"{ID} [] (comment='{new_value}')")

    def test_delete(self):
        # Creates a thing (without using the thing_update()) method
        qrbug_main.Thing.get(ID)

        # Tests around deleting an instance
        self.check(qrbug_main.Thing, f'{ID} [] ()')
        qrbug_main.thing_del(ID)
        self.check(qrbug_main.Thing, '')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug_main.Thing, f"0 [] (comment='A comment, it seems')")
