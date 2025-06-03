import qrbug.init
import qrbug

def init_db():
    qrbug.thing_update('thing_child',
        location='thing_child_location',
        comment='thing_child_comment')
    qrbug.user_add('user_parent', 'user_child')
    qrbug.thing_add('thing_parent', 'thing_child')
    qrbug.thing_add('thing_parent_parent', 'thing_parent')
    qrbug.failure_update('fail1',
        value='first failure',
        display_type=qrbug.DisplayTypes.text,
        ask_confirm=False,
        restricted_to_group_id='group'
    )


class TestSelector(qrbug.TestCase):

    def check(self, selector, user, thing, failure, expected):
        result = selector.is_ok(
            qrbug.User[user], qrbug.Thing[thing], qrbug.Failure[failure])
        self.assertEqual(result, expected, selector.expr)

    def test_thing(self):
        init_db()

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
        self.check(s, "user_child", "thing_child" , "fail1", '/thing_parent_parent/thing_parent/thing_child')
        self.check(s, "user_child", "thing_parent", "fail1", '/thing_parent_parent/thing_parent')
        self.check(s, "user_child", "thing_parent_parent", "fail1", '/thing_parent_parent')

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

        s = qrbug.selector_update('location',
            '{"class":"Thing", "attr":"location", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_child_location')

        s = qrbug.selector_update('comment',
            '{"class":"Thing", "attr":"comment", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_child_comment')

        self.tearDown()

    def test_failure(self):
        init_db()

        s = qrbug.selector_update('failure value',
            '{"class":"Failure", "attr":"value", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'first failure')

        s = qrbug.selector_update('failure display_type',
            '{"class":"Failure", "attr":"display_type", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", qrbug.DisplayTypes.text)

        s = qrbug.selector_update('failure ask_confirm',
            '{"class":"Failure", "attr":"ask_confirm", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", False)

        s = qrbug.selector_update('failure restricted_to_group_id',
            '{"class":"Failure", "attr":"restricted_to_group_id", "test":"true"}')
        self.check(s, "user_child", "thing_child" , "fail1", 'group')

        self.tearDown()


    def test_or_and(self):
        init_db()

        s = qrbug.selector_update('thing_id or failure_id',
            '[0, {"class":"Thing", "attr":"id", "test":"true"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", 'thing_child')

        s = qrbug.selector_update('not thing_id or failure_id',
            '[0, {"class":"Thing", "attr":"id", "test":"false"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", 'fail1')

        s = qrbug.selector_update('not thing_id or not failure_id',
            '[0, {"class":"Thing", "attr":"id", "test":"false"}, {"class":"Failure", "attr":"id", "test":"false"}]')
        self.check(s, "user_child", "thing_child" , "fail1", False)

        s = qrbug.selector_update('thing_id and failure_id',
            '[1, {"class":"Thing", "attr":"id", "test":"true"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", 'fail1')

        s = qrbug.selector_update('not thing_id and failure_id',
            '[1, {"class":"Thing", "attr":"id", "test":"false"}, {"class":"Failure", "attr":"id", "test":"true"}]')
        self.check(s, "user_child", "thing_child" , "fail1", False)

        s = qrbug.selector_update('not thing_id and not failure_id',
            '[1, {"class":"Thing", "attr":"id", "test":"true"}, {"class":"Failure", "attr":"id", "test":"false"}]')
        self.check(s, "user_child", "thing_child" , "fail1", False)


        self.tearDown()

        
