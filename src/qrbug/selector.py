from typing import Optional
import ast

import qrbug

OPERATORS = [' or ', ' and ']

ITEMS = {
    'Incident': 'incident'                      , # The incident sent to dispatcher
    'Thing': 'incident.thing'                   , # Its thing
    'Failure': 'incident.failure'               , # Its failure
    'User': 'qrbug.User[incident.active[-1].login]', # User triggering the last report
    'Selector': 'qrbug.Selector[%ID%]'          , # Selector from 'id' attr
    # The 3 next values
    'SourceThing': 'source.thing'               , # Its thing
    'SourceFailure': 'source.failure'           , # Its failure
    'SourceUser': 'qrbug.User.get(report.login)', # User triggering the API incident
    # TODO :
    #   * Incident other attributes (IP, date...)
    #   * Incident closed/open
}

ATTRIBUTES = {
    'path'        : '.path()'                       , # Tree subclasses
    'id'          : '.id'                           , # Any
    'comment'     : '.comment'                      , # Thing
    'is_ok'       : '.is_ok(incident,source,report)', # Selector
    'value'       : '.value'                        , # Failure
    'display_type': '.display_type'                 , # Failure
    'ask_confirm' : '.ask_confirm'                  , # Failure
    'allowed'     : '.allowed'                      , # Failure
}

TESTS = {
    '<': '{attr} < {value}',
    '>': '{attr} > {value}',
    '<=': '{attr} <= {value}',
    '>=': '{attr} >= {value}',
    '=': '{attr} == {value}',
    'is': '{attr}.id == {value}',
    'in': '{attr}.inside({value})',
    'in_or_equal': '{attr}.inside_or_equal({value})',
    'is_concerned': 'incident.is_for({attr})',
    'pending_feedback': 'incident.pending_feedback',
    'active': 'incident.active',
    'contains': '{value} in {attr}',
    'true': '{attr}',
    'false': 'not({attr})',
}

def compil_expr(expr):
    if isinstance(expr, list):
        return '(' + OPERATORS[expr[0]].join(compil_expr(item) for item in expr[1:]) + ')'

    if 'class' in expr:
        item = ITEMS[expr['class']]
        if 'id' in expr:
            item = item.replace('%ID%', repr(expr['id']))
        if 'attr' in expr:
            item += ATTRIBUTES[expr['attr']]
    else:
        item = 'BUG'

    test = TESTS[expr['test']].format(attr=item, value=repr(expr.get('value', '')))
    return f'({test})'

class Selector(qrbug.Editable):
    instances: dict[str, "Selector"] = {}
    compiled = None

    def __init__(self, selector_id: str, expression: str):
        self.id = selector_id
        self.expression = expression
        self.instances[selector_id] = self

    def is_ok(self, incident: 'qrbug.Incident', source=None, report=None) -> bool:
        if not self.compiled:
            self.expr = compil_expr(ast.literal_eval(self.expression)) # For regtests
            self.compiled = compile(self.expr, self.expr, 'eval')
        # There are not Thing for for Edit incident
        # if incident.thing is None:
        #     raise Exception(f'Unknown thing: «{incident.thing_id}»')
        if incident.failure is None:
            raise Exception(f'Unknown failure: «{incident.failure_id}»')
        # print(len(incident.active), source, self.expr)
        # print(eval(self.compiled, {'incident': incident, 'qrbug': qrbug, 'source': source, 'report': report}))
        return eval(self.compiled, {'incident': incident, 'qrbug': qrbug, 'source': source, 'report': report})

    def __class_getitem__(cls, selector_id: str) -> Optional["Selector"]:
        return cls.instances.get(selector_id, None)


def selector(selector_id: str, expression: str) -> Selector:
    return Selector(selector_id, expression)


qrbug.Selector = Selector
qrbug.selector_update = selector
