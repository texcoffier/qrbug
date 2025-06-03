import asyncio
import qrbug.init
import qrbug

def init_db():
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

class File:
    def __init__(self, lines):
        self.lines = lines
    async def write(self, data):
        self.lines.append(data.decode('utf-8'))

class Request:
    def __init__(self):
        self.lines = []
        self.response = File(self.lines)

class TestAction(qrbug.TestCase):

    def check(self, dispatcher, incident, expected):
        request = Request()
        asyncio.run(dispatcher.run(incident, request))
        self.assertEqual(request.lines, expected)

    def test_simple_dispatch(self):
        init_db()

        d1 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true',
            group_id='user_parent', incidents='')
        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, ['Start\n', 'thing_child,fail1,ip1,None,,None\n', 'End\n'])

        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, ['Start\n', 'thing_child,fail1,ip2,None,,None\n', 'End\n'])

        # The 2 incidents are open, send all incidents to action
        d2 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true',
            group_id='user_parent', incidents='true')
        self.check(d2, i2, [
            'Start\n',
            'thing_child,fail1,ip1,None,,None\n',
            'thing_child,fail1,ip2,None,,None\n',
            'End\n'
            ])

        # The 2 incidents are open, send no incidents to action
        d2 = qrbug.dispatcher_update('simple', action_id='echo', selector_id='true',
            group_id='user_parent', incidents='false')
        self.check(d2, i2, [])

        self.tearDown()

    def test_hour_dispatch(self):
        init_db()

        d1 = qrbug.dispatcher_update('morning', action_id='echo', selector_id='07:00',
            group_id='user_parent', incidents='true')

        i1 = qrbug.Incident.open('thing_child', 'fail1', 'ip1', 'login1')
        self.check(d1, i1, [])
        i2 = qrbug.Incident.open('thing_child', 'fail1', 'ip2', 'login2')
        self.check(d1, i2, [])
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(d1, morning, [
            'Start\n',
            'thing_child,fail1,ip1,None,,None\n',
            'thing_child,fail1,ip2,None,,None\n',
            'debug,07:00,,None,,None\n',
            'End\n'
            ])
        morning = qrbug.Incident.open('debug', '07:00', '', '')
        self.check(d1, morning, [
            'Start\n',
            'thing_child,fail1,ip1,None,,None\n',
            'thing_child,fail1,ip2,None,,None\n',
            'debug,07:00,,None,,None\n',
            'debug,07:00,,None,,None\n',
            'End\n'
            ])

        self.tearDown()


        
