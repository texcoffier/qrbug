from typing import Generator


class TreeHealth:
    def __init__(self, children_ids: list[str], parent_id: str):
        # Counts how many times each ID is repeated in the classes' children, if they are repeated more than once
        # They key is the ID, and the value is how many times it is repeated
        self.repeated_ids: dict[str, int] = {}

        # Whether the tree contains a reference to itself within its children
        self.is_cyclic: bool = False

        # Checks the IDs given as parameter
        self.count_repeated_ids(children_ids)
        self.check_is_cyclic(children_ids, parent_id)

    def count_repeated_ids(self, children_ids: list[str]) -> dict[str, int]:
        self.repeated_ids.clear()

        for child_id in children_ids:
            child_id_count = children_ids.count(child_id)
            if child_id_count > 1:
                self.repeated_ids[child_id] = child_id_count

        return self.repeated_ids

    def check_is_cyclic(self, children_ids: list[str], parent_id: str) -> bool:
        self.is_cyclic = parent_id in children_ids
        return self.is_cyclic

    @property
    def is_healthy(self) -> bool:
        return self.is_cyclic is False and self.repeated_ids == {}

    def __bool__(self) -> bool:
        return self.is_healthy


class Tree:
    instances: dict[str, "Tree"] = {}

    def __init__(self, tree_id: str) -> None:
        self.id: str = tree_id
        self.children_ids: list[str] = []

    def add_child(self, child: "Tree") -> None:
        # assert child.id not in self.children_ids, f"{child.id} is already a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.append(child.id)

    def remove_child(self, child: "Tree") -> None:
        # assert child.id in self.children_ids, f"{child.id} is not a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.remove(child.id)

    @classmethod
    def get(cls, tree_id: str) -> "Tree":
        if tree_id not in cls.instances:
            cls.instances[tree_id] = cls(tree_id)
        return cls.instances[tree_id]

    def dump(self) -> str:
        return f"{self.id} {self.children_ids}"

    @classmethod
    def dump_all(cls) -> Generator[str, None, None]:
        yield from (instance.dump() for key, instance in Tree.instances.items())

    def check(self) -> TreeHealth:
        return TreeHealth(self.children_ids, self.id)

    @classmethod
    def check_all(cls) -> Generator[TreeHealth, None, None]:
        yield from (TreeHealth(instance.children_ids, instance.id) for instance in Tree.instances.values())

    @classmethod
    def update_tree(cls, tree_id: str, **kwargs):
        # Gets the tree the user asked for (or creates one with the corresponding ID if it did not exist)
        tree = cls.get(tree_id)

        # Sets the new data of the tree
        for arg, value in kwargs.items():
            assert hasattr(cls, arg), f"Class {cls.__name__} has no attribute '{arg}', do not attempt to update it"
            assert arg != "instances", f"Cannot update instances of {cls.__name__} class, please do not attempt"
            setattr(tree, arg, value)

        return tree

    @classmethod
    def add_parenting_link(cls, parent_id: str, child_id: str):
        cls.get(parent_id).add_child(cls.get(child_id))

    @classmethod
    def remove_parenting_link(cls, parent_id: str, child_id: str):
        cls.get(parent_id).remove_child(cls.get(child_id))