import html
import qrbug

class Concerned:
    instances: dict["SelectorId", set['UserId']] = {}

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

    def get_failures(self, as_html: bool = True) -> str:
        root_failure = qrbug.Failure['concerned']
        if as_html:
            return root_failure.get_hierarchy_representation_html(self)
        else:
            return root_failure.get_hierarchy_representation()

    def __class_getitem__(cls, selector_id: str) -> set["UserId"]:
        return cls.instances.get(selector_id, None)

qrbug.concerned_add = Concerned.concerned_add
qrbug.concerned_del = Concerned.concerned_del
qrbug.Concerned = Concerned
