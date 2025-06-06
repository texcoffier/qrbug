from typing import Optional
import ast

import qrbug

OPERATORS = [' or ', ' and ']

ITEMS = {
    'Incident': 'incident'                         , # The incident sent to dispatcher
    'Thing': 'incident.thing'                      , # Its thing
    'Failure': 'incident.failure'                  , # Its failure
    'User': 'qrbug.User[incident.login]'           , # User triggering the incident
    'SourceThing': 'source.thing'                  , # Its thing
    'SourceFailure': 'source.failure'              , # Its failure
    'SourceUser': 'qrbug.User.get(source.active[-1].login)', # User triggering the incident
    'Selector': 'qrbug.Selector[%ID%]'             , # Selector from 'id' attr
    # TODO :
    #   * Incident other attributes (IP, date...)
    #   * Incident closed/open
}

ATTRIBUTES = {
    'path'                   : '.path()'                     , # Tree subclasses
    'id'                     : '.id'                         , # Any
    'location'               : '.location'                   , # Thing
    'comment'                : '.comment'                    , # Thing
    'is_ok'                  : '.is_ok(incident)'            , # Selector
    'value'                  : '.value'                      , # Failure
    'display_type'           : '.display_type'               , # Failure
    'ask_confirm'            : '.ask_confirm'                , # Failure
    'restricted_to_group_id' : '.restricted_to_group_id'     , # Failure
    'to'                     : '.group_id'                   , # Dispatcher
}

TESTS = {
    '<': '%ATTR% < %VALUE%',
    '>': '%ATTR% > %VALUE%',
    '<=': '%ATTR% <= %VALUE%',
    '>=': '%ATTR% >= %VALUE%',
    '=': '%ATTR% == %VALUE%',
    'in': '%ATTR%.inside(%VALUE%)',
    'in_or_equal': '%ATTR%.inside_or_equal(%VALUE%)',
    'is_concerned': 'incident.is_for(%ATTR%)',
    'contains': '%VALUE% in %ATTR%',
    'true': '%ATTR%',
    'false': 'not %ATTR%',
}

def compil_expr(expr):
    if isinstance(expr, list):
        return '(' + OPERATORS[expr[0]].join(compil_expr(item) for item in expr[1:]) + ')'

    item = ITEMS[expr['class']]
    if 'id' in expr:
        item = item.replace('%ID%', repr(expr['id']))
    if 'attr' in expr:
        item += ATTRIBUTES[expr['attr']]
    return TESTS[expr['test']].replace('%ATTR%', item).replace('%VALUE%', repr(expr.get('value', '')))

class Selector:
    instances: dict[str, "Selector"] = {}
    compiled = None

    def __init__(self, selector_id: str, expression: str):
        self.id = selector_id
        self.expression = expression
        self.instances[selector_id] = self

    def is_ok(self, incident: 'qrbug.Incident', source=None, dispatcher=None) -> bool:
        if not self.compiled:
            self.expr = compil_expr(ast.literal_eval(self.expression)) # For regtests
            self.compiled = compile(self.expr, '', 'eval')

        if incident.thing is None:
            raise Exception(f'Unknown thing: «{incident.thing_id}»')
        if incident.failure is None:
            raise Exception(f'Unknown failure: «{incident.failure_id}»')
        return eval(self.compiled, {"incident": incident, 'qrbug': qrbug, 'source': source, 'dispatcher': dispatcher})

    def __class_getitem__(cls, selector_id: str) -> Optional["Selector"]:
        return cls.instances.get(selector_id, None)


def selector(selector_id: str, expression: str) -> Selector:
    return Selector(selector_id, expression)


qrbug.Selector = Selector
qrbug.selector_update = selector
