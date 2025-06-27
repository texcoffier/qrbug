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
    textarea = enum.auto()
    input    = enum.auto()
    boolean  = enum.auto()
    display  = enum.auto()
    checkbox = enum.auto()
    datalist = enum.auto()


def element(failure: "Failure", thing, in_place=False, destroy=None, datalist_id: str = None, force_value: str = None, is_popup: bool = False):
    display_type = failure.display_type
    ask_confirm = html.escape(failure.ask_confirm or '')
    common = f'failureid="{html.escape(failure.id)}" thingid="{html.escape(thing.id)}" what="{thing.__class__.__name__.lower()}" ask_confirm="{ask_confirm}"'
    failure_value = force_value if force_value else failure.value
    if display_type == DisplayTypes.text:
        return  f'<p {common}>{failure_value}</p>'
    if display_type == DisplayTypes.redirect:
        return  f'<a {common} href="{failure_value}">{failure_value}</p>'
    if display_type == DisplayTypes.button:
        destroy_val = ''
        if destroy:
            destroy_val = f' predefined_value="{html.escape(destroy)}"'
        return f'<div {common}{destroy_val} class="button" onclick="register_incident(this,{int(in_place)})"><BOX>{failure_value}</BOX></div>'

    value = ''
    if failure.inside('edit') and '-' in failure.id:
        attr = getattr(thing, failure.id.split('-', 1)[1], None)
        if attr is None:
            value = ''
        else:
            value = html.escape(str(attr))
    in_place = int(in_place)
    if display_type == DisplayTypes.boolean:
        element = f'<select {common} class="button" onchange="register_incident(this,{in_place})"><option value="False">Non</option><option value="True">Oui</option></select></div>'
        if attr:
            element = element.replace('value="True"', 'value="True" selected')
        else:
            element = element.replace('value="False"', 'value="True" selected')
        if not in_place:
            element = f'<div class="input">{failure_value} : {element}</div>'
        return element
    if display_type == DisplayTypes.display:
        element = [f'<select {common} class="button" onchange="register_incident(this,{in_place})">']
        for v in DisplayTypes:
            element.append(f'<option value="{v.name}"{" selected" if attr == v else ""}>{v.name}</option>')
        element.append('</select>')
        element = ''.join(element)
        if not in_place:
            element = f'<div class="input">{failure_value} : {element}</div>'
        return element
    if is_popup or display_type == DisplayTypes.textarea:
        popup_type = "ASK_VALUE_TYPE_TEXTAREA"
        if display_type == DisplayTypes.input:
            popup_type = "ASK_VALUE_TYPE_INPUT"
        elif display_type == DisplayTypes.datalist:
            popup_type = f"ASK_VALUE_TYPE_DATALIST,{repr(datalist_id)}"
        return f'<div {common} class="button" value="{value}" onclick="ask_value(this,{in_place},{popup_type})"><BOX>{failure_value}</BOX></div>'
    if display_type == DisplayTypes.checkbox:
        element = f'<input {common} type="checkbox" autocomplete="off" onclick="register_incident(this,{in_place})">'
        if attr:
            element = element.replace('<input', '<input checked')
        if not in_place:
            element = f'<div class="input">{failure_value} : {element}</div>'
        return element
    if display_type == DisplayTypes.input or display_type == DisplayTypes.datalist:
        if destroy:
            common += f' predefined_value="{html.escape(destroy)}"'
            return f'''<div {common} class="delete" style="display:inline-block"
                ><a onclick="javascript:show(this)">{html.escape(destroy)}</a>
                <button onclick="register_incident(this,1)">×</button></div>'''
        input_list_id = ''
        if display_type == DisplayTypes.datalist:
            input_list_id = f' list="datalist_{datalist_id}"'
        return f'''<div class="input">{'' if in_place else failure_value}
        <div><input {common}{input_list_id} value="{value}" autocomplete="off" onkeypress="if (event.key=='Enter') register_incident(this,{in_place})"
        ><button {common} onclick="register_incident(this, {in_place})">⬆</button></div></div>'''
    raise ValueError("Unknown display type")

qrbug.element = element

class Failure(qrbug.Tree):
    """
    A failure of a thing.
    """
    instances: dict[FailureId, "Failure"] = {}

    # Default values
    value       : str           = ''
    display_type: DisplayTypes  = DisplayTypes.text
    ask_confirm : bool          = False
    allowed     : qrbug.UserId  = 'true' # No restriction

    def init(self):
        self.value = f"VALEUR_NON_DEFINIE POUR «{self.id}»"

    def _local_dump(self) -> str:
        return f'val:{repr(self.value)} type:{self.display_type.name if self.display_type is not None else None} ' \
               f'confirm:{self.ask_confirm} allowed:{self.allowed}'

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
                representation.append(
                        f"[allowed={current_failure.allowed.ljust(GROUP_JUSTIFICATION)}]"
                    )
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
            representation.append(element(failure, thing))
            if failure.children_ids:
                representation.append(f'<div class="children">')
                for failure_id in failure.children_ids:
                    recursively_build_failures_list(failure_id)
                representation.append(f"</div>\n")

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

if __name__ == "__main__":
    failure_update("0", value="Testing title", display_type=Text)
    print(Failure["0"].dump())
