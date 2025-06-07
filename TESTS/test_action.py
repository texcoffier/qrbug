import asyncio
import qrbug.init
import qrbug

class TestAction(qrbug.TestCase):

    def setUp(self):
        qrbug.thing_update('thing_child',
            location='thing_child_location',
            comment='thing_child_comment')
        qrbug.user_add('user_parent', 'user_child')
        qrbug.thing_add('thing_parent', 'thing_child')
        qrbug.thing_add('thing_parent_parent', 'thing_parent')
        qrbug.thing_update('debug')
        qrbug.failure_update('fail1',
            value='first failure',
            display_type=qrbug.DisplayTypes.text,
            ask_confirm=False,
            restricted_to_group_id='group'
        )
        qrbug.failure_update('07:00', restricted_to_group_id='system')
        qrbug.selector_update('true', '{"class": "Thing", "attr":"id", "test": "true"}')
        qrbug.selector_update('false', '{"class": "Thing", "attr":"id", "test": "false"}')
        qrbug.selector_update('07:00', '{"class": "Failure", "attr":"id", "test": "=", "value": "07:00"}')
        qrbug.action_update('echo', 'echo.py')
        qrbug.action_update('close', 'close.py')

    def check(self, dispatcher, incident, expected):
        request = qrbug.Request()
        asyncio.run(dispatcher.run(incident, request))
        self.assertEqual(request.lines, expected)

    def test_simple_dispatch(self):
        d1 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='')
        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, ['<pre>\n', 'Active thing_child,fail1,ip1,,login1,None\n', '</pre>\n'])

        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, ['<pre>\n', 'Active thing_child,fail1,ip1,,login1,None\n', 'Active thing_child,fail1,ip2,,login2,None\n', '</pre>\n'])

        # The 2 incidents are open, s</pre> all incidents to action
        d2 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='true')
        self.check(d2, i2, [
            '<pre>\n',
            'Active thing_child,fail1,ip1,,login1,None\n',
            'Active thing_child,fail1,ip2,,login2,None\n',
            '</pre>\n'
            ])

        # The 2 incidents are open, s</pre> no incidents to action
        d2 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true', incidents='false')
        self.check(d2, i2, [])

    def test_hour_dispatch(self):
        d1 = qrbug.dispatcher_update('morning', action_id='echo', selector_id='07:00', incidents='true')

        close = qrbug.dispatcher_update('close', action_id='close', selector_id='07:00')

        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, [])
        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, [])

        # Close '07:00' after dispatching
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(d1, morning, [
            '<pre>\n',
            'Active thing_child,fail1,ip1,,login1,None\n',
            'Active thing_child,fail1,ip2,,login2,None\n',
            'Active debug,07:00,,,,None\n',
            '</pre>\n'
            ])
        self.check(close, morning, ['«Clôture de /07:00» «VALEUR_NON_DEFINIE POUR «07:00»»\n'])

        # Close '07:00' after dispatching
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(d1, morning, [
            '<pre>\n',
            'Active thing_child,fail1,ip1,,login1,None\n',
            'Active thing_child,fail1,ip2,,login2,None\n',
            'Active debug,07:00,,,,None\n',
            'Pending feedback debug,07:00,,,,\n',
            '</pre>\n'
            ])
        self.check(close, morning, ['«Clôture de /07:00» «VALEUR_NON_DEFINIE POUR «07:00»»\n'])

        # Close '07:00' before dispatching
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(close, morning, ['«Clôture de /07:00» «VALEUR_NON_DEFINIE POUR «07:00»»\n'])
        self.check(d1, morning, [
            '<pre>\n',
            'Active thing_child,fail1,ip1,,login1,None\n',
            'Active thing_child,fail1,ip2,,login2,None\n',
            '</pre>\n'
            ])

    def test_list_incident(self):
        qrbug.action_update('list', 'list.py')
        qrbug.failure_update('list-Incident')

        qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        trigger = qrbug.Incident.open('debug', 'list-Incident', 'ip2', 'login2')
        dispatcher = qrbug.dispatcher_update('show_incidents', action_id='echo',
            selector_id='true', incidents='true')

        request = qrbug.Request()
        asyncio.run(dispatcher.run(trigger, request))
        self.assertEqual(request.lines, [
            '<pre>\n',
            'Active thing_child,fail1,ip1,,login1,None\n',
            'Active debug,list-Incident,ip2,,login2,None\n',
            '</pre>\n'
            ])

        # Fix the problem
        qrbug.Incident.close('thing_child', 'fail1', 'ip1', 'fixer_login')
        request = qrbug.Request()
        asyncio.run(dispatcher.run(trigger, request))
        self.assertEqual(request.lines, [
            '<pre>\n',
            'Active debug,list-Incident,ip2,,login2,None\n',
            '</pre>\n'
            ])

        # Pending user feeback
        qrbug.selector_update('with-pending-feedback', '{"test": "pending_feedback"}')
        list_pending = qrbug.dispatcher_update('show_pending', action_id='echo',
            selector_id='true', incidents='with-pending-feedback')
        request = qrbug.Request()
        asyncio.run(list_pending.run(trigger, request))
        self.assertEqual(request.lines, [
            '<pre>\n',
            'Pending feedback thing_child,fail1,ip1,,login1,fixer_login\n',
            '</pre>\n'
            ])

        # Send pending feedback
        qrbug.action_update('pending_feedback', 'pending_feedback.py')
        send_pending = qrbug.dispatcher_update('send_pending', action_id='pending_feedback',
            selector_id='true', incidents='with-pending-feedback')
        request = qrbug.Request()
        asyncio.run(send_pending.run(trigger, request))
        self.assertEqual(request.lines, [
            '<pre>\n',
            'SEND FEEDBACK FOR thing_child,fail1,ip1,,login1,fixer_login\n',
            '</pre>\n'
            ])

        # Pending user feeback
        request = qrbug.Request()
        asyncio.run(list_pending.run(trigger, request))
        self.assertEqual(request.lines, [])
