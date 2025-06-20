import qrbug

class Editable:
    def path(self):
        return f'The title must be defined in «{self.__class__.__name__}.path()»'

    def get_failures(self, secret = 0, as_html: bool = True) -> str:
        # The root failure for edition is the class name in lowercase
        root_failure = qrbug.Failure[self.__class__.__name__.lower()]
        if as_html:
            return root_failure.get_hierarchy_representation_html(self, secret)
        else:
            return root_failure.get_hierarchy_representation()

    def __class_getitem__(cls, an_id: str) -> "Editable":
        return cls.instances.get(an_id, None)

qrbug.Editable = Editable
