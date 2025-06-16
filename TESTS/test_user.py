import qrbug.init
import qrbug


class TestUser(qrbug.TestCase):
    def test_creation(self):
        self.check(qrbug.User,
                   '')
        qrbug.user_update('0')
        qrbug.user_update('1')
        qrbug.user_add('0', '1')
        self.check(qrbug.User,
                   "0 ['1'] ()\n"
                   '1 [] ()')

    def test_deletion(self):
        qrbug.user_update('0')
        qrbug.user_update('1')
        qrbug.user_add('0', '1') # test_creation checked if it is working
        qrbug.user_remove('0', '1')
        self.check(qrbug.User,
                   '0 [] ()\n'
                   '1 [] ()')

    def test_with_db(self):
        self.load_config()
        self.check(qrbug.User,
                   '0 [] ()\n'
                   '1 [] ()')
