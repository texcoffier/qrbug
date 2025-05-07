from typing import Generator


class Tree:
    instances: dict[str, "Tree"] = {}

    def __init__(self, tree_id: str) -> None:
        self.id: str = tree_id
        self.children_ids: set[str] = set()

    def add_child(self, child: "Tree") -> None:
        # assert child.id not in self.children_ids, f"{child.id} is already a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.add(child.id)

    def remove_child(self, child: "Tree") -> None:
        # assert child.id in self.children_ids, f"{child.id} is not a child of {self.id}"
        # assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.remove(child.id)

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
        if tree_id not in cls.instances:
            cls.instances[tree_id] = cls(tree_id)
        return cls.instances[tree_id]

    def dump(self) -> str:
        return f"{self.id} {self.children_ids}"

    @classmethod
    def dump_all(cls) -> Generator[str, None, None]:
        return (instance.dump() for (key, instance) in Tree.instances.items())

    def check(self) -> str:
        """
        Returns an error message about the health of the data structure.
        """
        all_children = self.get_all_children_ids()
        if self.id in all_children:
            return "WARNING: Cyclic children imports !"
        return "OK."

    @classmethod
    def check_all(cls) -> Generator[str, None, None]:
        return (instance.check() for instance in Tree.instances.values())

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