import asyncio
import qrbug.init
import qrbug



class TestSelector(qrbug.TestCase):

    def runtest(self, failure, action):
        qrbug.failure_update(failure)
        qrbug.selector_update('edit-selector',
            '{"class":"Failure", "test":"in_or_equal", "value": "%s"}' % failure)
        dispatcher = qrbug.dispatcher_update('do edit',
            action_id=action, selector_id='edit-selector')
        request = qrbug.Request()
        trigger = qrbug.Incident.open('a-selector', failure, 'ip2', 'login2', 'john.doe')
        asyncio.run(dispatcher.run(trigger, request))
        return request.lines

    def test_concerned(self):
        qrbug.selector_update('a-selector', '{"test":"true"}')
        qrbug.concerned_add('a-selector', 'nobody') # Do not do this in real
        qrbug.action_update('edit_concerned', 'edit_concerned.py')

        lines = self.runtest('concerned-add', 'edit_concerned')
        self.assertEqual(lines,
            ["L'utilisateur/groupe «john.doe» est maintenant concerné par le sélecteur «a-selector»\n"])
        self.assertEqual(qrbug.Concerned.instances['a-selector'].users, {'nobody', 'john.doe'})

        lines = self.runtest('concerned-del', 'edit_concerned')
        self.assertEqual(lines,
            ["L'utilisateur/groupe «john.doe» n'est plus concerné par le sélecteur «a-selector»\n"])
        self.assertEqual(qrbug.Concerned.instances['a-selector'].users, {'nobody'})
