import qrbug.main as qrbug_main


class TestUser(qrbug_main.TestCase):
    def test_creation(self):
        self.check(qrbug_main.User,
                   '')
        qrbug_main.user_add('0', '1')
        self.check(qrbug_main.User,
                   "0 ['1'] User()\n"
                   '1 [] User()')

    def test_deletion(self):
        qrbug_main.user_add('0', '1') # test_creation checked if it is working
        qrbug_main.user_remove('0', '1')
        self.check(qrbug_main.User,
                   '0 [] User()\n'
                   '1 [] User()')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug_main.User,
                   '0 [] User()\n'
                   '1 [] User()')
