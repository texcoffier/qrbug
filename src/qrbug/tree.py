import enum
from typing import Generator, Optional, List
from io import StringIO

import qrbug


class Tree(qrbug.Editable):
    instances: dict[str, "Tree"] = None
    sorted_instances: List["Tree"] = []

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
            parent = self.instances[next(iter(self.parent_ids))]
            return f'{parent.path()} {self.id.removeprefix(parent.id)}'
        return f'{self.id}'

    def inside(self, node: "TreeId"):
        """Consider that a node is not inside itself"""
        for parent in self.parent_ids:
            if parent == node:
                return True
            if self.instances[parent].inside(node):
                return True
        return False

    def inside_or_equal(self, node: "TreeId"):
        """Inside he group or is the group"""
        return self.inside(node) or self.id == node

    def add_child(self, child: "Tree") -> None:
        """Assume the child is not present"""
        self.children_ids.append(child.id)
        child.parent_ids.add(self.id)

    def move_child_before(self, child_id: "TreeId", before_id: "TreeId") -> None:
        # assert child.id not in self.children_ids, f"{child.id} is already a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.remove(child_id)
        self.children_ids.insert(self.children_ids.index(before_id), child_id)

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
                add_child_to_set(self.instances[child_id])
                all_children.add(child_id)

        all_children = set()
        add_child_to_set(self)
        return all_children

    def get_sorted_children_ids(self, max_depth: int = -1) -> Generator[str, None, None]:
        def add_child_to_list(node, depth: int = 0):
            if depth >= max_depth and max_depth != -1:
                return
            for child_id in sorted(node.children_ids):
                yield child_id
                yield from add_child_to_list(self.instances[child_id], depth + 1)
        yield self.id
        yield from add_child_to_list(self)

    def walk(self, go_in, go_out):
        done = set()
        def walk_(node):
            go_in(node)
            if node.id not in done:
                done.add(node.id)
                for child_id in node.children_ids:
                    walk_(node.instances[child_id])
            go_out(node)
        walk_(self)

    @classmethod
    def roots(self):
        for node in self.instances.values():
            if not node.parent_ids:
                yield node

    @classmethod
    def get_or_create(cls, tree_id: str) -> "Tree":
        """ Returns the given tree instance if it exists, or CREATES IT then returns it otherwise. """
        if tree_id not in cls.instances:
            cls.instances[tree_id] = cls(tree_id)
            cls.sorted_instances = None
        return cls.instances[tree_id]

    @classmethod
    def get_sorted_instances(cls) -> "List[Tree]":
        if not cls.sorted_instances:
            cls.sorted_instances = sorted(cls.instances.values(), key=lambda x: x.id)
        return cls.sorted_instances

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
        if tree_id in cls.instances:
            if kwargs:
                cls.instances[tree_id].__dict__.update(kwargs)
        else:
            cls.sorted_instances = None
            if kwargs:
                tree = cls.instances[tree_id] = cls(tree_id)
                tree.__dict__.update(kwargs)
            else:
                 cls.instances[tree_id] = cls(tree_id)

        # Sets the new data of the tree
        # for arg, value in kwargs.items():
        #     assert hasattr(cls, arg), f"Class {cls.__name__} has no attribute '{arg}', do not attempt to update it"
        #     assert arg != "instances", f"Cannot update instances of {cls.__name__} class, please do not attempt"
        #     setattr(tree, arg, value)

    @classmethod
    def add_parenting_link(cls, parent_id: str, child_id: str):
        cls.instances[parent_id].add_child(cls.instances[child_id])

    @classmethod
    def remove_parenting_link(cls, parent_id: str, child_id: str):
        cls.instances[parent_id].remove_child(cls.instances[child_id])

    @classmethod
    def move_before(cls, parent_id: str, child_id: str, before_id: str):
        cls.instances[parent_id].move_child_before(child_id, before_id)

qrbug.Tree = Tree
