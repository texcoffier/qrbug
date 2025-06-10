"""
Defines all kinds of failures that can happen on a thing.
"""
import html
from typing import Optional, TypeAlias
import enum

import qrbug

FailureId: TypeAlias = str


class DisplayTypes(enum.Enum):
    text     = enum.auto()
    button   = enum.auto()
    redirect = enum.auto()
    input    = enum.auto()

def element(failure: "Failure", thing, in_place=False):
    display_type = failure.display_type
    common = f'failureid="{failure.id}" thingid="{thing.id}" what="{thing.__class__.__name__.lower()}"'
    if display_type == DisplayTypes.text:
        return  f'<p {common}>{failure.value}</p>'
    elif display_type == DisplayTypes.redirect:
        return  f'<a {common} href="{failure.value}">{failure.value}</p>'
    elif display_type == DisplayTypes.button:
        return f'<div {common} class="button" onclick="register_incident(this)"><BOX>{failure.value}</BOX></div>'
    elif display_type == DisplayTypes.input:
        value = ''
        if failure.inside('edit') and '-' in failure.id:
            attr = getattr(thing, failure.id.split('-', 1)[1], None)
            if attr is not None:
                value = html.escape(attr)
        in_place = int(in_place)
        return f'''<div class="input">{'' if in_place else failure.value}
        <div><input {common} value="{value}" autocomplete="off" onkeypress="if (event.key=='Enter') register_incident(this,{in_place})">
        <button {common} onclick="register_incident(this, {in_place})">-&gt;</button></div></div>'''
    raise ValueError("Unknown display type")

qrbug.element = element

class Failure(qrbug.Tree):
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}

    # Default values
    value                  : Optional[str]          = ''
    display_type           : Optional[DisplayTypes] = DisplayTypes.text
    ask_confirm            : Optional[bool]         = True
    restricted_to_group_id : Optional[qrbug.UserId] = None

    def init(self):
        self.value = f"VALEUR_NON_DEFINIE POUR «{self.id}»"

    def _local_dump(self) -> str:
        # short_names = {
        #     'value': 'val',
        #     'display_type': 'type',
        #     'ask_confirm': 'confirm',
        #     'restricted_to_group_id': 'group',
        # }
        # return self.get_representation(attributes_short=short_names)
        return f'val:{repr(self.value)} type:{self.display_type.name if self.display_type is not None else None} ' \
               f'confirm:{self.ask_confirm} group:{self.restricted_to_group_id}'

    def get_hierarchy_representation(self) -> str:
        """
        Returns the hierarchy representation of this failure as raw text.
        """
        representation: list[str] = []

        INDENTATION_SIZE: int = 2
        SHOW_ADDITIONAL_ATTRIBUTES_INFO: bool = True
        GROUP_JUSTIFICATION: int = 8
        VALUE_JUSTIFICATION: int = 50
        DISPLAY_TYPE_WIDTH: int = 10
        ID_WIDTH: int = max(len(failure_id) for failure_id in self.instances)

        def recursively_build_failures_list(failure_id: str, depth: int = 0) -> None:
            INDENTATION_DEPTH: int = depth * INDENTATION_SIZE

            current_failure: Optional["Failure"] = Failure[failure_id]
            if current_failure is None:
                return

            representation.append(
                f"{' ' * INDENTATION_DEPTH}- {current_failure.value.ljust(VALUE_JUSTIFICATION - INDENTATION_DEPTH)}"
            )
            if SHOW_ADDITIONAL_ATTRIBUTES_INFO:
                representation.append(
                    "\t\t"
                    f"[ {current_failure.id.ljust(ID_WIDTH)} ]\t"
                    f"[{current_failure.display_type.name.center(DISPLAY_TYPE_WIDTH)}]\t"
                    f"[ask_confirm?={'YES' if current_failure.ask_confirm else 'NO '}]\t"
                )
                if current_failure.restricted_to_group_id is not None:
                    representation.append(
                        f"[group={current_failure.restricted_to_group_id.ljust(GROUP_JUSTIFICATION)}]"
                    )
                else:
                    representation.append(f"[{'No group'.center(GROUP_JUSTIFICATION + len('group='))}]")
            representation.append("\n")

            # We sort by display type then by value, so that the text failures are
            # always shown first (headers), followed by the buttons, the redirects, and
            # the input fields (which are usually just the "Other" answer)
            # We have to sort this instead of just using the loop as-is because sets have no defined order,
            # which means if we don't sort this, the result is going to come out different every time
            child_failures_list = [
                Failure[failure]
                for failure in current_failure.children_ids
            ]
            child_failures_list.sort(key=lambda e: (e.display_type.value, e.value))

            for child_failure in child_failures_list:
                recursively_build_failures_list(child_failure.id, depth + 1)

        recursively_build_failures_list(self.id)
        return ''.join(representation)


    def get_hierarchy_representation_html(self, thing, use_template: bool = True) -> str:
        """
        Returns a representation of the whole hierarchy of this failure as a webpage.
        :param thing_id: The id of the thing that could be targeted by this failure.
        :param use_template: If true, return this failure's HTML using a template file.
        """
        path = thing.path()
        representation: list[str] = [
            '<TITLE>', path, '</TITLE>',
            '<H1>', path, '</H1>'
            ]

        # TODO : Caching ?
        if use_template:
            html_template = qrbug.get_template()

        def recursively_build_failures_list(failure_id: str) -> None:
            failure = Failure[failure_id]
            representation.append(element(failure, thing))
            if failure.children_ids:
                representation.append(f'<div class="children">')
                for failure_id in failure.children_ids:
                    recursively_build_failures_list(failure_id)
                representation.append(f"</div>\n")

        recursively_build_failures_list(self.id)
        if use_template:
            return html_template.replace("%REPRESENTATION%", ''.join(representation))
        else:
            return ''.join(representation)


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


def failure_add(parent: FailureId, child: FailureId, before_id:str='') -> None:
    """
    Adds a new child to an existing failure.
    :param parent: The ID of the failure to add the child to.
    :param child: The ID of the child failure.
    """
    Failure.add_parenting_link(parent, child, before_id)


def failure_remove(parent: FailureId, child: FailureId) -> None:
    """
    Removes the parenting link from a failure to another.
    :param parent: The ID of the failure to remove the child from.
    :param child: The ID of the failure to be removed.
    """
    Failure.remove_parenting_link(parent, child)


qrbug.Failure = Failure
qrbug.FailureId = FailureId
qrbug.DisplayTypes = DisplayTypes
qrbug.failure_update = failure_update
qrbug.failure_add = failure_add
qrbug.failure_remove = failure_remove

if __name__ == "__main__":
    failure_update("0", value="Testing title", display_type=DisplayTypes.text)
    print(Failure.get("0").dump())
