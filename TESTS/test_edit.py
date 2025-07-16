import asyncio
import qrbug.init
import qrbug



class TestEdit(qrbug.TestCase):
    def setUp(self):
        qrbug.exec_code_file(qrbug.DEFAULT_DB_PATH, qrbug.CONFIGS)

    def runtest(self, failure, dispatcher, value=''):
        qrbug.selector_update('?edit-selector',
            '{"class":"SourceFailure", "test":"in_or_equal", "value": "%s"}' % failure)
        trigger = qrbug.Incident.open('a-selector', failure, 'ip2', '@admin', value)
        request = qrbug.Request(trigger)
        asyncio.run(qrbug.Dispatcher[dispatcher].run(trigger, request, []))
        return request.lines

    def test_concerned(self):
        qrbug.selector_update('a-selector', '{"test":"true"}')
        qrbug.selector_concerned_add('a-selector', 'nobody')

        lines = self.runtest('$selector-concerned-add', '!edit-selector', 'john.doe')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nL'utilisateur/groupe «john.doe» est maintenant concerné par le sélecteur «a-selector»\n"])
        self.assertEqual(qrbug.Selector.instances['a-selector'].concerned, {'nobody', 'john.doe'})

        lines = self.runtest('$selector-concerned-del', '!edit-selector', 'john.doe')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nL'utilisateur/groupe «john.doe» n'est plus concerné par le sélecteur «a-selector»\n"])
        self.assertEqual(qrbug.Selector.instances['a-selector'].concerned, {'nobody'})

    def test_dispatcher(self):
        lines = self.runtest('$dispatcher', '!edit-dispatcher')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Dispatcher\n"])

        self.assertEqual(qrbug.Failure['$dispatcher'].get_hierarchy_representation().count('ask_confirm'), 5)

    def test_failure(self):
        qrbug.failure_update('a-selector') # Failure to edit

        lines = self.runtest('$failure-value', '!edit-failure', 'New value')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nLe titre de la panne «a-selector» est maintenant «New value»\n"])
        self.assertEqual(qrbug.Failure.instances['a-selector'].value, 'New value')

        lines = self.runtest('$failure-display_type', '!edit-failure', 'BAD')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nLa valeur de «a-selector . $failure-display_type» est inchangé.\nCar invalide."])
        self.assertEqual(qrbug.Failure.instances['a-selector'].value, 'New value')

        lines = self.runtest('$failure-display_type', '!edit-failure', 'button')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nLe type d'affichage de «a-selector» est maintenant «button»\n"])
        self.assertEqual(qrbug.Failure.instances['a-selector'].display_type.name, 'button')

        lines = self.runtest('$failure-ask_confirm', '!edit-failure', 'Are you sure?')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nOn demande confirmation avant d'envoyer la panne «a-selector»\n"])
        self.assertEqual(qrbug.Failure.instances['a-selector'].ask_confirm, 'Are you sure?')

        lines = self.runtest('$failure', '!edit-failure')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Failure\n"])

        self.assertEqual(qrbug.Failure['$failure'].get_hierarchy_representation().count('ask_confirm'), 7)

    def test_selector(self):
        lines = self.runtest('$selector', '!edit-selector')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Selector\n"])
        self.assertEqual(qrbug.Failure['$selector'].get_hierarchy_representation().count('ask_confirm'), 5)

    def test_thing(self):
        lines = self.runtest('$thing', '!edit-thing')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Thing\n"])
        self.assertEqual(qrbug.Failure['$thing'].get_hierarchy_representation().count('ask_confirm'), 6)

    def test_user(self):
        lines = self.runtest('$user', '!edit-user')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for User\n"])
        self.assertEqual(qrbug.Failure['$user'].get_hierarchy_representation().count('ask_confirm'), 4)

    def test_action(self):
        qrbug.action_update('a-selector', 'close.py') # Action to edit

        lines = self.runtest('$action-python_script', '!edit-action', 'echo.py')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nL'action «a-selector» lance maintenant le script «echo.py»\n"])

        lines = self.runtest('$action-python_script', '!edit-action', 'nodefinedscript.py')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nLe script Python «nodefinedscript.py» n'existe pas.\n"])

        lines = self.runtest('$action', '!edit-action')
        self.assertEqual(lines,
            ["<!DOCTYPE html>\nUnexpected edit failure for Action\n"])

        self.assertEqual(qrbug.Failure['$action'].get_hierarchy_representation().count('ask_confirm'), 2)
