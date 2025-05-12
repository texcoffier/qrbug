from qrbug.user import User, user_add, user_remove
from qrbug.main import TestCase


class TestUser(TestCase):
    def test_creation(self):
        self.check(User,
                   '')
        user_add("0", "1")
        self.check(User,
                   "0 ['1'] User()\n"
                   "1 [] User()")

    def test_deletion(self):
        user_add("0", "1") # test_creation checked if it is working
        user_remove("0", "1")
        self.check(User,
                   "0 [] User()\n"
                   "1 [] User()")

    def test_with_db(self):
        self.load_config()
        self.check(User,
                   "0 [] User()\n"
                   "1 [] User()")
