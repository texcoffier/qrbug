import html
import json
from typing import Optional, List
import qrbug

def link_to_object(what, thing_id, request, label=None):
    thing_id = html.escape(thing_id)
    if label is None:
        label = thing_id
    return f'<a target="_blank" href="{what}={thing_id}?secret={request.secret.secret}">{label}</a>'

def link_to_active(thing_id, request):
    active = sum(len(i.active) for i in qrbug.Incident.instances[thing_id].values())
    if not active:
        return ''
    return f'<a target="_blank" href="?failure-id=thing-incidents-active&thing-id={thing_id}&secret={request.secret.secret}">{active}</a>'

def link_to_finished(thing_id, request):
    finished = sum(len(i.finished) for i in qrbug.Incident.instances[thing_id].values())
    if not finished:
        return ''
    return f'<a target="_blank" href="?failure-id=thing-incidents&thing-id={thing_id}&secret={request.secret.secret}">{finished}</a>'

def display_tree(texts, request, what, columns):
    failures = []
    for failure_definition in columns:
        failure = failure_definition.lstrip('|')
        vertical = (failure != failure_definition)
        failure, datalist = (failure.split(' datalist=') + [None])[:2]
        failures.append((qrbug.Failure[failure], vertical, datalist))
    texts.append('''
    <style>
    .vert { writing-mode: sideways-lr; font-weight: normal; font-size: 60%; }
    </style>
    <table><tr>
    ''')
    what_name = what.__name__.lower()
    texts.append('<th>')
    if what_name == 'thing':
        texts.append('<th>')
    for failure, vertical, _data_list in failures:
        if vertical:
            vertical = ' class="vert"'
        else:
            vertical = ''
        if failure.id == 'thing-del-failure':
            texts.append('<th colspan="2">Actives<br>Inactives')
        if failure.id == 'selector-concerned-del':
            texts.append('<th>Éditeur de sélecteur')
        texts.append(f'<th{vertical}>{failure.value}')
    def go_in(node):
        texts.append('<tr><td>')
        if what_name == 'thing':
            texts.append(f'<input type="checkbox" autocomplete="off" class="qr_thing_checkboxes" id="qr_thing_checkbox_{node.id}" onclick="qr_select(this.checked, {repr(node.id)});" /><td>')
        texts.append(go_in.indent)
        texts.append(link_to_object(what_name, node.id, request))
        for failure, _vertical, datalist in failures:
            texts.append('<td>')
            if failure.id.endswith('remove'):
                if go_in.parents:
                    texts.append(qrbug.element(
                        failure, node, in_place=True,
                        force_value='×', destroy=go_in.parents[-1]))
            elif failure.id == 'thing-del-failure': # Insert multiple columns
                thing_incident = qrbug.Incident.instances.get(node.id, None)
                if thing_incident:
                    texts.append(link_to_active(node.id, request))
                    texts.append('<td>')
                    texts.append(link_to_finished(node.id, request))
                else:
                    texts.append('<td>')
                texts.append('<td>')
                for failure_id in node.failure_ids:
                    texts.append(' ')
                    texts.append(qrbug.element(failure, node, destroy=failure_id))
            elif failure.id == 'selector-concerned-del':
                texts.append('<script>add_selector(')
                texts.append(json.dumps(node.id))
                texts.append(',')
                texts.append(node.expression)
                texts.append(');\n</script><td>')
                texts.append(' '.join(qrbug.element(failure, node, destroy=user)
                                      for user in node.concerned))
            else:
                texts.append(qrbug.element(failure, node, in_place=True, datalist_id=datalist))
        texts.append('</tr>')
        go_in.indent += '    '
        go_in.parents.append(node.id)
    def go_out(_node):
        go_in.indent = go_in.indent[:-4]
        go_in.parents.pop()
    go_in.indent = ''
    go_in.parents = []
    if hasattr(what, 'roots'):
        for tree in what.roots():
            tree.walk(go_in, go_out, do_sort=True)
    else:
        for node in what.instances.values():
            go_in(node)
            go_out(node)
    texts.append('</table>')
    return set(datalist for _, _, datalist in failures if datalist)

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = [f'<title>{incident.failure.value}</title><h1>{incident.failure.value}</h1>']
    if what is qrbug.Thing:
        texts.append('<p>Cochez les objets puis cliquez sur le bouton pour générer une feuille de QR codes (lignes × colonne) : ')
        texts.append(' '.join(
            f'<div class="button" style="display: inline;" onclick="qr(this)">{html.escape(failure.split("_")[-1])}</div>'
            for failure in qrbug.Failure['generate_qr'].children_ids
        ))
        texts.append('<p id="qr_code_gen_error_field"></p></p>')
        datalists_to_load = display_tree(texts, request, what,
            ('thing-comment', 'thing-del-failure', 'thing-add-failure datalist=Failure',
            '|||thing-remove', 'thing-add datalist=Thing'))
    elif what is qrbug.Failure:
        datalists_to_load = display_tree(texts, request, what,
                        ('failure-value', 'failure-ask_confirm',
                        '|||failure-display_type',
                        '|||failure-remove', 'failure-add datalist=Failure'))
    elif what is qrbug.User:
        datalists_to_load = display_tree(texts, request, what,
            ('|||user-remove', 'user-add datalist=User'))
    elif what is qrbug.Dispatcher:
        dispatcher_new = qrbug.Failure['dispatcher-new']
        texts.append('<table><tr><td>')
        texts.append(dispatcher_new.value)
        texts.append(qrbug.element(dispatcher_new, qrbug.Thing['GUI'], in_place=True))
        texts.append('</tr></table>')
        datalists_to_load = display_tree(texts, request, what,
            ('dispatcher-selector_id datalist=Selector',
                'dispatcher-incidents datalist=Selector',
                'dispatcher-action_id datalist=Action'))
    elif what is qrbug.Action:
        datalists_to_load = display_tree(texts, request, what,
            ('action-python_script datalist=ActionScripts',))
    elif what is qrbug.Selector:
        texts.append(f'''
        <script>
        var LISTS = {{
            'datalist_Failure': {list(qrbug.Failure.instances)},
            'datalist_User': {list(qrbug.User.instances)},
            'datalist_Selector': {list(qrbug.Selector.instances)},
            'datalist_Thing': {list(qrbug.Thing.instances)}
            }};
        {qrbug.SELECTOR_SCRIPT_FUNCTIONS.read_text()}
        </script>
        ''')
        datalists_to_load = display_tree(texts, request, what,
            ('selector-concerned-del', 'selector-concerned-add datalist=User'))
    elif what is qrbug.Incident:
        texts.append('''
        <BODY class="real">
        <style>
        #api:checked ~ TABLE TR TD.real, #real:checked ~ TABLE TR TD.api { display: none;}
        TD.api { opacity: 0.5;}
        LABEL:hover { background: #EEE }
        TABLE { border-spacing: 0px }
        TABLE, TABLE TD, TABLE TH { border: 1px solid #BBB }
        </style>
        <input id="real" type="radio" name="what" checked>
        <label for="real">vrais incidents.</label>
        <input id="api" type="radio" name="what">
        <label for="api">appels à l'API.</label>
        <input id="all" type="radio" name="what">
        <label for="all">tous les incidents.</label>
        <table><tr><th>Objet<th>Actives<th>Réparés<th>Panne<th>Active<th>Réparée
        ''')
        for thing_id, failures in sorted(what.instances.items()):
            active = link_to_active(thing_id, request)
            finished = link_to_finished(thing_id, request)
            is_real = False
            is_api = False
            for failure in failures.values():
                if failure.active or failure.finished:
                    is_real = True
                else:
                    is_api = True
            if is_real and not is_api:
                classe = '<td class="real"'
            elif not is_real and is_api:
                classe = '<td class="api"'
            else:
                classe = '<td '
            texts.append(f'''<tr>{classe} rowspan="{len(failures)}">
            {link_to_object("thing", thing_id, request)}
            {classe} rowspan="{len(failures)}">{active}
            {classe} rowspan="{len(failures)}">{finished}''')
            prefix = ''
            for failure_id, failure in failures.items():
                if failure.active or failure.finished:
                    classe = '<td class="real">'
                else:
                    classe = '<td class="api">'
                texts.append(f'''{prefix}{classe}{link_to_object("failure", failure_id, request)}
                {classe}{len(failure.active)}
                {classe}{len(failure.finished)}
                </tr>
                ''')
            prefix = classe
        texts.append('</table>')
        datalists_to_load = ()
    else:
        for node in what.instances.values() if hasattr(what, 'instances') else what.active:
            try:
                texts.append(html.escape(node.dump()) + '<br>')
            except: # pylint: disable=bare-except
                texts.append(html.escape(str(node)) + '<br>')
        datalists_to_load = ()
    texts = [qrbug.get_template(request, datalists_to_load).replace('%REPRESENTATION%', ''.join(texts))]
    await request.write(''.join(texts))
    return None
