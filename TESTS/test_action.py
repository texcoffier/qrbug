import asyncio
import qrbug.init
import qrbug

class TestAction(qrbug.TestCase):

    def setUp(self):
        qrbug.thing_update('thing_child',
            comment='thing_child_comment')
        qrbug.user_add('user_parent', 'user_child')
        qrbug.thing_add('thing_parent', 'thing_child')
        qrbug.thing_add('thing_parent_parent', 'thing_parent')
        qrbug.thing_update('debug')
        qrbug.failure_update('fail1',
            value='first failure',
            display_type=qrbug.DisplayTypes.text,
            ask_confirm=False,
            allowed='group'
        )
        qrbug.failure_update('07:00', allowed='system')
        qrbug.selector_update('active', '{"test": "active"}')
        qrbug.selector_update('true', '{"class": "Thing", "test": "true"}')
        qrbug.selector_update('false', '{"class": "Thing", "test": "false"}')
        qrbug.selector_update('07:00', '{"class": "Failure", "test": "is", "value": "07:00"}')
        qrbug.action_update('echo', 'echo.py')
        qrbug.action_update('close', 'close.py')

    def check(self, dispatcher, incident, expected, clean=True):
        request = qrbug.Request()
        asyncio.run(dispatcher.run(incident, request, []))
        # print(''.join(request.lines))
        if clean:
            lines = [line
                    .split('<td', 1)[1]
                    .split('>', 1)[1]
                    .split('</tr>', 1)[0]
                    .split('\n', 1)[0]
                    .replace('<td>', ',')
                    .replace('<br>', ' ')
                    .replace('\xa0', '')
                    .strip()
                    for line in ''.join(request.lines).split('<tr')[1:]
                    ]
        else:
            lines = request.lines
        self.assertEqual(lines, expected)

    def test_simple_dispatch(self):
        d1 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='')
        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, ['«thing_child» «fail1»', 'ip1,,login1'])

        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, ['«thing_child» «fail1»', 'ip1,,login1', 'ip2,,login2'])

        # The 2 incidents are open, s</pre> all incidents to action
        d2 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='active')
        self.check(d2, i2, ['«thing_child» «fail1»', 'ip1,,login1', 'ip2,,login2'])

        # The 2 incidents are open, s</pre> no incidents to action
        d2 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='false')
        self.check(d2, i2, [])

    def test_hour_dispatch(self):
        d1 = qrbug.dispatcher_update('morning', action_id='echo', selector_id='07:00', incidents='active')

        close = qrbug.dispatcher_update('close', action_id='close', selector_id='07:00')

        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, [])
        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, [])

        # Close '07:00' after dispatching
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(d1, morning, [
            '«thing_child» «fail1»',
            'ip1,,login1',
            'ip2,,login2',
            '«debug» «07:00»',
            ',,'])
        self.check(close, morning, ['«Clôture de 07:00» «VALEUR_NON_DEFINIE POUR «07:00»»\n'], clean=False)

        # Close '07:00' after dispatching
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(d1, morning, [
            '«thing_child» «fail1»',
            'ip1,,login1',
            'ip2,,login2',
            '«debug» «07:00»',
            ',,',
            ',,,'])
        self.check(close, morning, ['«Clôture de 07:00» «VALEUR_NON_DEFINIE POUR «07:00»»\n'], clean=False)

        # Close '07:00' before dispatching
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(close, morning, ['«Clôture de 07:00» «VALEUR_NON_DEFINIE POUR «07:00»»\n'], clean=False)
        self.check(d1, morning, ['«thing_child» «fail1»', 'ip1,,login1', 'ip2,,login2'])

    def test_list_incident(self):
        qrbug.action_update('list', 'list.py')
        qrbug.failure_update('list-Incident')

        qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        trigger = qrbug.Incident.open('debug', 'list-Incident', 'ip2', 'login2')
        dispatcher = qrbug.dispatcher_update('show_incidents', action_id='echo',
            selector_id='true', incidents='active')
        self.check(dispatcher, trigger, [
            '«thing_child» «fail1»',
            'ip1,,login1',
            '«debug» «list-Incident»',
            'ip2,,login2'])

        # Fix the problem
        qrbug.Incident.close('thing_child', 'fail1', 'ip1', 'fixer_login')
        self.check(dispatcher, trigger, ['«debug» «list-Incident»', 'ip2,,login2'])

        # Pending user feeback
        qrbug.selector_update('with-pending-feedback', '{"test": "pending_feedback"}')
        list_pending = qrbug.dispatcher_update('show_pending', action_id='echo',
            selector_id='true', incidents='with-pending-feedback')
        self.check(list_pending, trigger, ['«thing_child» «fail1»', 'ip1,,login1,fixer_login'])

        # Send pending feedback
        qrbug.action_update('pending_feedback', 'pending_feedback.py')
        send_pending = qrbug.dispatcher_update('send_pending', action_id='pending_feedback',
            selector_id='true', incidents='with-pending-feedback')
        request = qrbug.Request()
        asyncio.run(send_pending.run(trigger, request, []))
        self.assertEqual(request.lines, [
            '<pre>\n',
            'SEND FEEDBACK FOR thing_child,fail1,ip1,,login1,fixer_login\n',
            '</pre>\n'
            ])

        # Pending user feeback
        request = qrbug.Request()
        asyncio.run(list_pending.run(trigger, request, []))
        self.assertEqual(request.lines, [])
