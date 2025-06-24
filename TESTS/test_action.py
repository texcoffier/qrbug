import asyncio
import qrbug.init
import qrbug

class TestAction(qrbug.TestCase):

    def setUp(self):
        qrbug.user_update('user_parent')
        qrbug.user_update('user_child')
        qrbug.user_add('user_parent', 'user_child')
        qrbug.thing_update('thing_child', comment='thing_child_comment')
        qrbug.thing_update('thing_parent')
        qrbug.thing_update('thing_parent_parent')
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
        qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='')
        d1 = qrbug.Dispatcher['simple']
        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, ['«thing_child» «fail1»', 'ip1,,login1'])

        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, ['«thing_child» «fail1»', 'ip1,,login1', 'ip2,,login2'])

        # The 2 incidents are open,  all incidents to action
        qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='active')
        self.check(d1, i2, ['«thing_child» «fail1»', 'ip1,,login1', 'ip2,,login2'])

        # The 2 incidents are open,  no incidents to action
        qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='false')
        self.check(d1, i2, [])

    def test_hour_dispatch(self):
        qrbug.dispatcher_update('morning', action_id='echo', selector_id='07:00', incidents='active')
        d1 = qrbug.Dispatcher['morning']

        qrbug.dispatcher_update('close', action_id='close', selector_id='07:00')
        close = qrbug.Dispatcher['close']

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
        qrbug.dispatcher_update('show_incidents', action_id='echo',
            selector_id='true', incidents='active')
        dispatcher = qrbug.Dispatcher['show_incidents']
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
        qrbug.dispatcher_update('show_pending', action_id='echo',
            selector_id='true', incidents='with-pending-feedback')
        list_pending = qrbug.Dispatcher['show_pending']
        self.check(list_pending, trigger, ['«thing_child» «fail1»', 'ip1,,login1,fixer_login'])

        # Send pending feedback
        qrbug.action_update('pending_feedback', 'pending_feedback.py')
        qrbug.dispatcher_update('send_pending', action_id='pending_feedback',
            selector_id='true', incidents='with-pending-feedback')
        send_pending = qrbug.Dispatcher['send_pending']
        request = qrbug.Request()
        asyncio.run(send_pending.run(trigger, request, []))
        self.assertTrue("login1@? (login1) <ul><li> thing_parent_parent/thing_parent/thing_child : first failure"
            in ''.join(request.lines))

        # Pending user feeback
        request = qrbug.Request()
        asyncio.run(list_pending.run(trigger, request, []))
        self.assertEqual(request.lines, ["L'automatisme «show_pending» n'a rien à faire, il n'est donc pas lancé"])
