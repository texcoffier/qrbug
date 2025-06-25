import html
import qrbug

class Concerned(qrbug.Editable):
    instances: dict["SelectorId", "Concerned"] = {}

    def __init__(self, selector_id):
        self.id = selector_id
        self.users = set()

    @classmethod
    def concerned_del(cls, selector_id, user_id):
        cls.instances[selector_id].users.discard(user_id)

    @classmethod
    def concerned_add(cls, selector_id, user_id):
        concerned = cls.instances.get(selector_id, None)
        if not concerned:
            concerned = cls.instances[selector_id] = Concerned(selector_id)
        concerned.users.add(user_id)

    def path(self):
        return f'Utilisateurs concernés par le sélecteur «{html.escape(self.id)}»'

qrbug.concerned_add = Concerned.concerned_add
qrbug.concerned_del = Concerned.concerned_del
qrbug.Concerned = Concerned
