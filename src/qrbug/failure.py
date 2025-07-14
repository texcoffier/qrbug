"""
Defines all kinds of failures that can happen on a thing.
"""
import html
from typing import Optional, TypeAlias
import enum

import qrbug

FailureId: TypeAlias = str


class DisplayTypes(enum.Enum):
    # For user report
    text     = enum.auto()
    button   = enum.auto()
    html     = enum.auto()
    textarea = enum.auto()
    # For object attribute editing
    input    = enum.auto()
    display  = enum.auto()
    datalist = enum.auto()


def element(failure: "Failure", thing, in_place=False, destroy=None, datalist_id: str = None, force_value: str = None):
    """
    :param destroy: usually sets up the predefined value of an element, in order to facilitate its destruction.
    :param force_value: actually sets the value of the element.
    """
    display_type = failure.display_type
    ask_confirm = html.escape(failure.ask_confirm or '')
    common = f'failureid="{html.escape(failure.id)}"' \
             f' thingid="{html.escape(thing.id)}"' \
             f' what="{thing.__class__.__name__.lower()}"' \
             f' ask_confirm="{ask_confirm}"' \
             f' in_place="{int(in_place)}"'

    ########################################
    # User interface for reporting failures
    ########################################

    failure_value = failure.value
    if not in_place:
        if display_type == DisplayTypes.text:
            return f'<p>{html.escape(failure_value)}</p>'
        if display_type == DisplayTypes.html:
            return failure_value
        if display_type == DisplayTypes.button:
            return f'<div {common} class="button" onclick="register_incident(this)">{failure_value}</div>'
        if display_type == DisplayTypes.textarea:
            return f'<div {common} class="button" onclick="ask_value(this)">{failure_value}</div>'
        before = f'<p style="background: #FFC">{failure_value} '
    else:
        before = ''
    ###########################################
    # User interface to edit object attributes
    ###########################################

    # Set the INPUT initial value to the current attribute
    assert failure.inside('$edit') and '-' in failure.id
    attr = getattr(thing, failure.id.split('-', 1)[1], None)
    if attr is None:
        value = ''
    else:
        value = html.escape(str(attr))

    # Display type used only for editing object attributes

    if display_type == DisplayTypes.display:
        text = [f'<select {common} class="button" onchange="register_incident(this)">']
        for v in DisplayTypes:
            text.append(f'<option value="{v.name}"{" selected" if attr == v else ""}>{v.name}</option>')
        text.append('</select>')
        return before + ''.join(text)
    if display_type in (DisplayTypes.input, DisplayTypes.datalist):
        if destroy:
            common += f' predefined_value="{html.escape(destroy)}"'
            return f'''{before}<div {common} class="delete" style="display:inline-block"
                ><a onclick="javascript:show(this)">{html.escape(destroy)}</a><div
                onclick="register_incident(this)">×</div></div>'''
        input_list_id = ''
        if display_type == DisplayTypes.datalist:
            input_list_id = f' list="datalist_{datalist_id}"'
        return f'''{before}<div class="input"><input {common}{input_list_id} value="{value}" autocomplete="off"
            onkeypress="if (event.key=='Enter') register_incident(this)"
            ><div {common} onclick="register_incident(this)">⬆</div></div>'''
    if display_type == DisplayTypes.button:
        assert destroy
        return f'''{before}<div {common} predefined_value="{html.escape(destroy)}"
            style="padding:0px" class="button"
            onclick="register_incident(this)">×</div>'''
    raise ValueError(f"Unknown display type: {display_type} {common}")

qrbug.element = element

class Failure(qrbug.Tree):
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}

    # Default values
    value       : str           = ''
    display_type: DisplayTypes  = DisplayTypes.text
    ask_confirm : str           = ''

    def init(self):
        self.value = f"VALEUR_NON_DEFINIE POUR «{self.id}»"

    def _local_dump(self) -> str:
        return f'val:{repr(self.value)}' \
               f' type:{self.display_type.name if self.display_type is not None else None}' \
               f' confirm:{self.ask_confirm}'

    def get_hierarchy_representation(self) -> str:
        """
        Returns the hierarchy representation of this failure as raw text.
        """
        representation: list[str] = []

        INDENTATION_SIZE: int = 2
        SHOW_ADDITIONAL_ATTRIBUTES_INFO: bool = True
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
            representation.append("\n")
            for failure_id in current_failure.children_ids:
                recursively_build_failures_list(failure_id, depth + 1)

        recursively_build_failures_list(self.id)
        return ''.join(representation)


    def get_hierarchy_representation_html(self, thing, secret = None, use_template: bool = True, done = None) -> str:
        """
        Returns a representation of the whole hierarchy of this failure as a webpage.
        :param thing_id: The id of the thing that could be targeted by this failure.
        :param use_template: If true, return this failure's HTML using a template file.
        """
        path = thing.path()
        representation: list[str] = [
            '<TITLE>', path, '</TITLE>',
            '<H1>', path, '</H1>',
            '<SCRIPT>var secret="', secret and secret.secret or '', '";</SCRIPT>'
            ]

        done = done or set()
        def recursively_build_failures_list(failure_id: str) -> None:
            if failure_id in done:
                return
            done.add(failure_id)
            failure = Failure[failure_id]
            representation.append(element(failure, thing) + ' ')
            if failure.children_ids:
                representation.append('<div class="children">')
                for failure_id in failure.children_ids:
                    recursively_build_failures_list(failure_id)
                representation.append('</div>\n')

        recursively_build_failures_list(self.id)
        if use_template:
            return qrbug.get_template().replace("%REPRESENTATION%", ''.join(representation))
        else:
            return ''.join(representation)

qrbug.Failure = Failure
qrbug.FailureId = FailureId
qrbug.DisplayTypes = DisplayTypes
qrbug.failure_update = Failure.update_attributes
qrbug.failure_add = Failure.add_parenting_link
qrbug.failure_remove = Failure.remove_parenting_link
qrbug.failure_move = Failure.move_before
