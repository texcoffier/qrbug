from typing import Generator


class Tree:
    instances: dict[str, "Tree"] = {}

    def __init__(self, tree_id: str) -> None:
        self.id: str = tree_id
        self.children_ids: list[str] = []

    def add_child(self, child: "Tree") -> None:
        assert child.id not in self.children_ids, f"{child.id} is already a child of {self.id}"
        assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
        self.children_ids.append(child.id)

    def remove_child(self, child: "Tree") -> None:
        assert child.id in self.children_ids, f"{child.id} is not a child of {self.id}"
        assert child.id != self.id, f"Cannot make {child.id} a child of itself !"
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
        yield from (f"{key}: {instance.dump()}" for key, instance in Tree.instances.items())