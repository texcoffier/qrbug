"""
Defines all kinds of failures that can happen on a thing.
"""
from typing import Optional, TypeAlias
import enum
from io import StringIO

from qrbug.user import UserId
from qrbug.tree import Tree

FailureId: TypeAlias = str


class DisplayTypes(enum.Enum):
    text     = enum.auto()
    button   = enum.auto()
    redirect = enum.auto()
    input    = enum.auto()


class Failure(Tree):
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}

    # Default values
    value                  : Optional[str]          = "VALEUR_NON_DEFINIE"
    display_type           : Optional[DisplayTypes] = DisplayTypes.text
    ask_confirm            : Optional[bool]         = True
    restricted_to_group_id : Optional[UserId]       = None

    def _local_dump(self) -> str:
        return self.get_representation()

    def get_hierarchy_representation(self) -> str:
        final_string_representation = StringIO()

        def recursively_build_failures_list(failure_id: str, depth: int = 0) -> None:
            nonlocal final_string_representation
            INDENTATION_SIZE: int = 2
            INDENTATION_DEPTH: int = depth * INDENTATION_SIZE
            SHOW_ADDITIONAL_ATTRIBUTES_INFO: bool = True
            GROUP_JUSTIFICATION: int = 8
            VALUE_JUSTIFICATION: int = 50
            DISPLAY_TYPE_JUSTIFICATION: int = 10

            current_failure: Optional["Failure"] = Failure.get_if_exists(failure_id)
            if current_failure is None:
                return

            final_string_representation.write(
                f"{' ' * INDENTATION_DEPTH}- {current_failure.value.ljust(VALUE_JUSTIFICATION - INDENTATION_DEPTH)}"
            )
            if SHOW_ADDITIONAL_ATTRIBUTES_INFO:
                final_string_representation.write(
                    "\t\t"
                    f"[{current_failure.display_type.name.center(DISPLAY_TYPE_JUSTIFICATION)}]\t"
                    f"[ask_confirm?={'YES' if current_failure.ask_confirm else 'NO '}]\t"
                )
                if current_failure.restricted_to_group_id is not None:
                    final_string_representation.write(
                        f"[group={current_failure.restricted_to_group_id.ljust(GROUP_JUSTIFICATION)}]"
                    )
                else:
                    final_string_representation.write(f"[{'No group'.center(GROUP_JUSTIFICATION + len("group="))}]")
            final_string_representation.write("\n")

            # We sort by display type then by value, so that the text failures are
            # always shown first (headers), followed by the buttons, the redirects, and
            # the input fields (which are usually just the "Other" answer)
            # We have to sort this instead of just using the loop as-is because sets have no defined order,
            # which means if we don't sort this, the result is going to come out different every time
            child_failures_list = [Failure.get_if_exists(failure) for failure in current_failure.children_ids]
            child_failures_list.sort(key=lambda e: (e.display_type.value, e.value))

            for child_failure in child_failures_list:
                recursively_build_failures_list(child_failure.id, depth + 1)

        recursively_build_failures_list(self.id)
        return final_string_representation.getvalue()


def failure_update(failure_id: FailureId, **kwargs) -> Failure:
    """
    Creates a new failure type, or modifies an existing one.
    :param failure_id: The ID of this failure type.
    :param value: The value of this failure.
    :param display_type: How to display this failure ? Text, button, message box... ?
    :param ask_confirm: Whether the user will have to confirm when pressing the button.
    :param restricted_to_group_id: If only a single group can report this failure type.
    """
    return Failure.update_attributes(failure_id, **kwargs)


def failure_add(parent: FailureId, child: FailureId) -> None:
    """
    Adds a new child to an existing failure.
    :param parent: The ID of the failure to add the child to.
    :param child: The ID of the child failure.
    """
    Failure.add_parenting_link(parent, child)


def failure_remove(parent: FailureId, child: FailureId) -> None:
    """
    Removes the parenting link from a failure to another.
    :param parent: The ID of the failure to remove the child from.
    :param child: The ID of the failure to be removed.
    """
    Failure.remove_parenting_link(parent, child)

if __name__ == "__main__":
    failure_update("0", value="Testing title", display_type=DisplayTypes.text)
    print(Failure.get("0").dump())
