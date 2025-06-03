import enum
from typing import Generator, Optional
from io import StringIO

import qrbug


class Tree:
    instances: dict[str, "Tree"] = None

    def __init__(self, tree_id: str) -> None:
        self.id: str = tree_id
        self.children_ids: list[str] = []
        self.parent_ids: set[str] = set()
        self.init()

    def init(self) -> None: # Redefined by subclass
        pass

    def path(self) -> str:
        """Return one of the path from root node, remove duplicate string"""
        if self.parent_ids:
            parent_path = self.instances[next(iter(self.parent_ids))].path()
            if self.id.startswith(parent_path):
                return self.id
            return f'{parent_path}/{self.id}'
        return f'/{self.id}'

    def inside(self, node: "TreeId"):
        """Consider that a node is not inside itself"""
        for parent in self.parent_ids:
            if parent == node:
                return True
            if self.instances[parent].inside(node):
                return True
        return False

    def add_child(self, child: "Tree", before: str = '') -> None:
        # assert child.id not in self.children_ids, f"{child.id} is already a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        if child.id in self.children_ids:
            self.children_ids.remove(child.id)
        if before in self.children_ids:
            self.children_ids.insert(self.children_ids.index(before), child.id)
        else:
            self.children_ids.append(child.id)
        child.parent_ids.add(self.id)

    def remove_child(self, child: "Tree") -> None:
        # assert child.id in self.children_ids, f"{child.id} is not a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.remove(child.id)
        child.parent_ids.remove(self.id)

    def get_all_children_ids(self) -> set[str]:
        def add_child_to_set(node):
            if node.id in all_children:
                return
            for child_id in node.children_ids:
                all_children.add(child_id)
                add_child_to_set(self.instances[child_id])

        all_children = set()
        add_child_to_set(self)
        return all_children

    @classmethod
    def get(cls, tree_id: str) -> "Tree":
        """ Returns the given tree instance if it exists, or CREATES IT then returns it otherwise. """
        if tree_id not in cls.instances:
            cls.instances[tree_id] = cls(tree_id)
        return cls.instances[tree_id]

    @classmethod
    def get_if_exists(cls, tree_id: str) -> Optional["Tree"]:
        """ Returns the given tree instance if it exists, or None otherwise. """
        if tree_id not in cls.instances:
            return None
        return cls.instances[tree_id]

    def dump(self) -> str:
        base = f"{self.id} {sorted(self.children_ids)}"
        if hasattr(self, "_local_dump"):
            base = f"{base} {self._local_dump()}"
        return base

    @classmethod
    def dump_all(cls) -> Generator[str, None, None]:
        return (instance.dump() for (key, instance) in cls.instances.items())

    def get_representation(self, display_class_name: bool = False, attributes_short: dict[str, str] = None) -> str:
        """
        Returns a string that can be used for _local_dump().
        """
        if attributes_short is None:
            attributes_short = {}

        dump = StringIO()
        if display_class_name:
            dump.write(self.__class__.__name__)
        dump.write("(")
        words = []
        for attribute in dir(self.__class__):
            attribute_value = getattr(self, attribute)
            if not attribute.startswith("_") and attribute != "instances" and not callable(attribute_value):
                if attribute_value is not None and getattr(self.__class__, attribute) != attribute_value:
                    if attribute in attributes_short:
                        attribute_name = attributes_short[attribute]
                    else:
                        attribute_name = attribute
                    if isinstance(attribute_value, enum.Enum):
                        attribute_value = attribute_value.name
                    words.append(f"{attribute_name}={repr(attribute_value)}")
        dump.write(", ".join(words))
        dump.write(")")
        return dump.getvalue()

    def check(self) -> str:
        """
        Returns an error message about the health of the data structure.
        """
        if self.id in self.get_all_children_ids():
            return "WARNING: Cyclic children imports !"
        return "OK."

    @classmethod
    def check_all(cls) -> Generator[str, None, None]:
        return (instance.check() for instance in Tree.instances.values())

    @classmethod
    def update_attributes(cls, tree_id: str, **kwargs):
        # Gets the tree the user asked for (or creates one with the corresponding ID if it did not exist)
        tree = cls.get(tree_id)

        # Sets the new data of the tree
        for arg, value in kwargs.items():
            assert hasattr(cls, arg), f"Class {cls.__name__} has no attribute '{arg}', do not attempt to update it"
            assert arg != "instances", f"Cannot update instances of {cls.__name__} class, please do not attempt"
            setattr(tree, arg, value)

        return tree

    @classmethod
    def add_parenting_link(cls, parent_id: str, child_id: str, before_id: str=''):
        cls.get(parent_id).add_child(cls.get(child_id), before_id)

    @classmethod
    def remove_parenting_link(cls, parent_id: str, child_id: str):
        cls.get(parent_id).remove_child(cls.get(child_id))

    def __class_getitem__(cls, tree_id: str) -> Optional["Tree"]:
        return cls.get_if_exists(tree_id)


qrbug.Tree = Tree
