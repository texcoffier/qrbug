from qrbug.thing import Thing, thing_update, thing_del
from qrbug.main import TestCase

ID = "0"


class TestThing(TestCase):
    def test_creation(self):
        self.check(Thing, '')
        thing_update(ID)
        self.check(Thing, f'{ID} [] {Thing.__name__}()')

    def test_update(self):
        # Creates a thing (without using the thing_update()) method
        Thing.get(ID)

        # Updates said thing
        new_value = "THIS IS A NEW VALUE FOR THE COMMENT"
        thing_update(ID, comment=new_value)
        self.check(Thing, f"{ID} [] {Thing.__name__}(comment='{new_value}')")

    def test_delete(self):
        # Creates a thing (without using the thing_update()) method
        Thing.get(ID)

        # Tests around deleting an instance
        self.check(Thing, f'{ID} [] {Thing.__name__}()')
        thing_del(ID)
        self.check(Thing, '')

    def test_with_db(self):
        self.load_config()
        self.check(Thing, f"0 [] {Thing.__name__}(comment='A comment, it seems')")
