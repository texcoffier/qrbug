import qrbug


class TestUser(qrbug.main.TestCase):
    def test_creation(self):
        self.check(qrbug.main.User,
                   '')
        qrbug.main.user_add('0', '1')
        self.check(qrbug.main.User,
                   "0 ['1'] ()\n"
                   '1 [] ()')

    def test_deletion(self):
        qrbug.main.user_add('0', '1') # test_creation checked if it is working
        qrbug.main.user_remove('0', '1')
        self.check(qrbug.main.User,
                   '0 [] ()\n'
                   '1 [] ()')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug.main.User,
                   '0 [] ()\n'
                   '1 [] ()')
