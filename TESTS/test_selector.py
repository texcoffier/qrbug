import asyncio
import qrbug.init
import qrbug



class TestSelector(qrbug.TestCase):

    def setUp(self):
        qrbug.user_update('user_parent')
        qrbug.user_update('user_child')
        qrbug.thing_update('thing_parent')
        qrbug.thing_update('thing_parent_parent')
        qrbug.thing_update('thing_child',
            comment='thing_child_comment')
        qrbug.user_add('user_parent', 'user_child')
        qrbug.thing_add('thing_parent', 'thing_child')
        qrbug.thing_add('thing_parent_parent', 'thing_parent')
        qrbug.failure_update('fail1',
            value='first failure',
            display_type=qrbug.DisplayTypes.text,
            ask_confirm=False,
            allowed='group'
        )

    def check(self, selector, login, thing_id, failure_id, expected):
        incident = qrbug.Incident.open(thing_id, failure_id, login=login,
                                       ip='no-ip', additional_info='no-comment')
        result = selector.is_ok(incident)
        self.assertEqual(result, expected, selector.expr)

    def test_thing(self):
        s = qrbug.selector_update('thing_id=thing_child',
            '{"class":"Thing", "attr":"id", "test":"=", "value":"thing_child"}')
        self.check(s, "user_child", "thing_child" , "fail1", True)
        self.check(s, "user_child", "thing_parent", "fail1", False)

        s = qrbug.selector_update('thing_id>t',
            '{"class":"Thing", "attr":"id", "test":">", "value":"t"}')
        self.check(s, "user_child", "thing_child" , "fail1", True)
        self.check(s, "user_child", "thing_parent", "fail1", True)

        s = qrbug.selector_update('thing_id contains t',
            '{"class":"Thing", "attr":"id", "test":"contains", "value":"t"}')
        self.check(s, "user_child", "thing_child" , "fail1", True)
        self.check(s, "user_child", "thing_parent", "fail1", True)

        s = qrbug.selector_update('thing_id contains p',
            '{"class":"Thing", "attr":"id", "test":"contains", "value":"p"}')
        self.check(s, "user_child", "thing_child" , "fail1", False)
        self.check(s, "user_child", "thing_parent", "fail1", True)

        s = qrbug.selector_update('thing_id True',
            '{"class":"Thing", "attr":"id", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_child')
        self.check(s, "user_child", "thing_parent", "fail1", 'thing_parent')

        s = qrbug.selector_update('thing_id path true',
            '{"class":"Thing", "attr":"path", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_parent_parent thing_parent thing_child')
        self.check(s, "user_child", "thing_parent", "fail1", 'thing_parent_parent thing_parent')
        self.check(s, "user_child", "thing_parent_parent", "fail1", 'thing_parent_parent')

        s = qrbug.selector_update('thing_id in thing_parent',
            '{"class":"Thing", "test":"in", "value": "thing_parent"}')
        self.check(s, "user_child", "thing_child" , "fail1", True)
        self.check(s, "user_child", "thing_parent", "fail1", False)
        self.check(s, "user_child", "thing_parent_parent", "fail1", False)

        s = qrbug.selector_update('thing_id in thing_parent_parent',
            '{"class":"Thing", "test":"in", "value": "thing_parent_parent"}')
        self.check(s, "user_child", "thing_child" , "fail1", True)
        self.check(s, "user_child", "thing_parent", "fail1", True)
        self.check(s, "user_child", "thing_parent_parent", "fail1", False)

        s = qrbug.selector_update('selector «thing_id contains p» is True',
            '{"class":"Selector", "id":"thing_id contains p", "attr":"is_ok", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", False)
        self.check(s, "user_child", "thing_parent", "fail1", True)

        s = qrbug.selector_update('comment',
            '{"class":"Thing", "attr":"comment", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_child_comment')


    def test_failure(self):
        s = qrbug.selector_update('failure value',
            '{"class":"Failure", "attr":"value", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'first failure')

        s = qrbug.selector_update('failure display_type',
            '{"class":"Failure", "attr":"display_type", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", qrbug.DisplayTypes.text)

        s = qrbug.selector_update('failure ask_confirm',
            '{"class":"Failure", "attr":"ask_confirm", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", False)

        s = qrbug.selector_update('failure allowed',
            '{"class":"Failure", "attr":"allowed", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'group')



    def test_or_and(self):
        s = qrbug.selector_update('thing_id or failure_id',
            '[0, {"class":"Thing", "attr":"id", "test":"true"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_child')

        s = qrbug.selector_update('not thing_id or failure_id',
            '[0, {"class":"Thing", "test":"false"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", 'fail1')

        s = qrbug.selector_update('not thing_id or not failure_id',
            '[0, {"class":"Thing", "test":"false"}, {"class":"Failure", "test":"false"}]')
        self.check(s, "user_child", "thing_child" , "fail1", False)

        s = qrbug.selector_update('thing_id and failure_id',
            '[1, {"class":"Thing", "attr":"id", "test":"true"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", 'fail1')

        s = qrbug.selector_update('not thing_id and failure_id',
            '[1, {"class":"Thing", "test":"false"}, {"class":"Failure", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", False)

        s = qrbug.selector_update('not thing_id and not failure_id',
            '[1, {"class":"Thing", "test":"true"}, {"class":"Failure", "test":"false"}]')
        self.check(s, "user_child", "thing_child" , "fail1", False)


    def test_is_for_user(self):
        # Record a report
        for_me = qrbug.selector_update('for-me', '{"class":"SourceUser", "test":"is_for_user"}')
        qrbug.selector_update('fail1', '{"class":"Failure", "test": "in_or_equal", "value": "fail1"}')
        qrbug.concerned_add('fail1', 'user_parent')
        incident = qrbug.Incident.open(
            'thing_child', 'fail1', login='no-login', ip='no-ip', additional_info='no-comment')

        # Get my incidents
        for user, expected in (('user_child', True), ('user_parent', True), ('somebody', False)):
            incident_trigger = qrbug.Incident.open(
                'a_thing', 'fail1', login=user, ip='no-ip', additional_info='no-comment')
            result = for_me.is_ok(incident, incident_trigger, incident_trigger.active[-1])
            self.assertEqual(result, expected, user)

    def test_pending_feedback(self):
        # Record a report
        dispatcher = qrbug.dispatcher_update('xxx', selector_id="true", action_id="echo")
        for_me = qrbug.selector_update('for-me', '{"class":"SourceUser", "test":"is_for_user"}')
        incident = qrbug.Incident.open(
            'thing_child', 'fail1', login='no-login', ip='no-ip', additional_info='no-comment')
        incident.incident_del()
        self.assertEqual(len(incident.pending_feedback['thing_child', 'fail1']), 1)

        selector = qrbug.selector_update('pending-feedback', '{"test":"pending_feedback"}')
        self.assertEqual(len(selector.is_ok(incident)), 1)
