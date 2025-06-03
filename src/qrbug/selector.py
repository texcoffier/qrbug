from typing import Optional
import ast

import qrbug

OPERATORS = [' or ', ' and ']

ITEMS = {
    'Incident': 'incident'                         , # The incident sent to dispatcher
    #'Thing': 'qrbug.Thing[incident.thing_id]'      , # Its thing
    'Thing': 'thing',
    #'Failure': 'qrbug.Failure[incident.failure_id]', # Its failure
    'Failure': 'failure',
    'User': 'qrbug.User[request.login]'            , # User triggering the incident
    'Selector': 'qrbug.Selector[%ID%]'             , # Selector from 'id' attr
}

ATTRIBUTES = {
    'path'                   : '.path()'                     , # Tree subclasses
    'id'                     : '.id'                         , # Any
    'location'               : '.location'                   , # Thing
    'comment'                : '.comment'                    , # Thing
    'is_ok'                  : '.is_ok(user, thing, failure)', # Selector
    'value'                  : '.value'                      , # Failure
    'display_type'           : '.display_type'               , # Failure
    'ask_confirm'            : '.ask_confirm'                , # Failure
    'restricted_to_group_id' : '.restricted_to_group_id'     , # Failure
}

TESTS = {
    '<': '%ATTR% < %VALUE%',
    '>': '%ATTR% > %VALUE%',
    '<=': '%ATTR% <= %VALUE%',
    '>=': '%ATTR% >= %VALUE%',
    '=': '%ATTR% == %VALUE%',
    'in': '%ATTR%.inside(%VALUE%)',
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

    def is_ok(self, user: 'qrbug.User', thing: 'qrbug.Thing', failure: 'qrbug.Failure') -> bool:
        if not self.compiled:
            self.expr = compil_expr(ast.literal_eval(self.expression)) # For regtests
            self.compiled = compile(self.expr, '', 'eval')
        return eval(self.compiled, {"user": user, "thing": thing, "failure": failure, 'qrbug': qrbug})

    def __class_getitem__(cls, selector_id: str) -> Optional["Selector"]:
        return cls.instances.get(selector_id, None)


def selector(selector_id: str, expression: str) -> Selector:
    return Selector(selector_id, expression)


qrbug.Selector = Selector
qrbug.selector_update = selector
