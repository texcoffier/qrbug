import asyncio
import qrbug.init
import qrbug



class TestEdit(qrbug.TestCase):
    def setUp(self):
        qrbug.exec_code_file(qrbug.DEFAULT_DB_PATH, qrbug.CONFIGS)

    def runtest(self, failure, dispatcher, value=''):
        qrbug.selector_update('edit-selector',
            '{"class":"Failure", "test":"in_or_equal", "value": "%s"}' % failure)
        trigger = qrbug.Incident.open('a-selector', failure, 'ip2', 'login2', value)
        request = qrbug.Request(trigger)
        asyncio.run(qrbug.Dispatcher[dispatcher].run(trigger, request, []))
        return request.lines

    def test_concerned(self):
        qrbug.selector_update('a-selector', '{"test":"true"}')
        qrbug.concerned_add('a-selector', 'nobody')

        lines = self.runtest('concerned-add', 'edit-concerned', 'john.doe')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nL'utilisateur/groupe «john.doe» est maintenant concerné par le sélecteur «a-selector»\n"])
        self.assertEqual(qrbug.Concerned.instances['a-selector'].users, {'nobody', 'john.doe'})

        lines = self.runtest('concerned-del', 'edit-concerned', 'john.doe')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nL'utilisateur/groupe «john.doe» n'est plus concerné par le sélecteur «a-selector»\n"])
        self.assertEqual(qrbug.Concerned.instances['a-selector'].users, {'nobody'})

        lines = self.runtest('concerned', 'edit-concerned')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Concerned\n"])

        self.assertTrue(qrbug.Failure['concerned'].get_hierarchy_representation()
            .count('ask_confirm') == 3)

    def test_dispatcher(self):
        lines = self.runtest('dispatcher', 'edit-dispatcher')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Dispatcher\n"])

        self.assertTrue(qrbug.Failure['dispatcher'].get_hierarchy_representation()
            .count('ask_confirm') == 1)

    def test_failure(self):
        lines = self.runtest('failure', 'edit-failure')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Failure\n"])

        self.assertTrue(qrbug.Failure['failure'].get_hierarchy_representation()
            .count('ask_confirm') == 1)

    def test_selector(self):
        lines = self.runtest('selector', 'edit-selector')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Selector\n"])

        self.assertTrue(qrbug.Failure['selector'].get_hierarchy_representation()
            .count('ask_confirm') == 1)

    def test_thing(self):
        lines = self.runtest('thing', 'edit-thing')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Thing\n"])
        self.assertTrue(qrbug.Failure['thing'].get_hierarchy_representation()
            .count('ask_confirm') == 2)

    def test_user(self):
        lines = self.runtest('user', 'edit-user')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for User\n"])

        self.assertTrue(qrbug.Failure['user'].get_hierarchy_representation()
            .count('ask_confirm') == 1)

    def test_action(self):
        qrbug.action_update('a-selector', 'close.py') # Action to edit

        lines = self.runtest('action-python_script', 'edit-action', 'echo.py')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nL'action «a-selector» lance maintenant le script «echo.py»\n"])

        lines = self.runtest('action-python_script', 'edit-action', 'nodefinedscript.py')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nLe script Python «nodefinedscript.py» n'existe pas.\n"])

        lines = self.runtest('action', 'edit-action')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Action\n"])

        self.assertTrue(qrbug.Failure['action'].get_hierarchy_representation()
            .count('ask_confirm') == 2)
