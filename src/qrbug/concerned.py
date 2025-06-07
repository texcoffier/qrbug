import collections
import qrbug

class Concerned:
    instances: dict["SelectorId", set['UserId']] = collections.defaultdict(set)

    @classmethod
    def concerned_del(cls, selector_id, user_id):
        return cls.instances[selector_id].pop(user_id, None)

    @classmethod
    def concerned_add(cls, selector_id, user_id):
        cls.instances[selector_id].add(user_id)

qrbug.concerned_add = Concerned.concerned_add
qrbug.concerned_del = Concerned.concerned_del
qrbug.Concerned = Concerned
