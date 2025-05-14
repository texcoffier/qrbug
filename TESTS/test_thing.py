import qrbug

ID = '0'


class TestThing(qrbug.TestCase):
    def test_creation(self):
        self.check(qrbug.Thing, '')
        qrbug.thing_update(ID)
        self.check(qrbug.Thing, f'{ID} [] loc:None failure:None comment:\'\'')

    def test_update(self):
        # Creates a thing (without using the thing_update()) method
        qrbug.Thing.get(ID)

        # Updates said thing
        new_value = 'THIS IS A NEW VALUE FOR THE COMMENT'
        qrbug.thing_update(ID, comment=new_value)
        self.check(qrbug.Thing, f"{ID} [] loc:None failure:None comment:'{new_value}'")

    def test_delete(self):
        # Creates a thing (without using the thing_update()) method
        qrbug.Thing.get(ID)

        # Tests around deleting an instance
        self.check(qrbug.Thing, f'{ID} [] loc:None failure:None comment:\'\'')
        qrbug.thing_del(ID)
        self.check(qrbug.Thing, '')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug.Thing, f"0 [] loc:None failure:None comment:'A comment, it seems'")
