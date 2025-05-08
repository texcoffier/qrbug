from qrbug.main import *
class TestUser(TestCase):
    def test_creation(self):
        self.check(User,
                   '')
        user_add("0", "1")
        self.check(User,
                   "0 ['1']\n"
                   "1 []")

    def test_deletion(self):
        user_add("0", "1") # test_creation checked if it is working
        user_remove("0", "1")
        self.check(User,
                   "0 []\n"
                   "1 []")

    def test_with_db(self):
        self.read_db()
        self.check(User,
                   "0 []\n"
                   "1 []")
