import html
import json
from typing import Optional, List

import qrbug


VERT_STYLE = '''<style>
            .vert { writing-mode: sideways-lr; font-weight: normal; font-size: 60%; }
            </style>'''

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

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = [f'<title>{incident.failure.value}</title><h1>{incident.failure.value}</h1>']

    if issubclass(what, qrbug.Tree):
        if what is qrbug.Thing:
            thing_comment = qrbug.Failure['thing-comment']
            texts.append('<p>Cochez les objets puis cliquez sur le bouton pour générer une feuille de QR codes (lignes × colonne) : ')
            texts.append(' '.join(
                f'<div class="button" style="display: inline;" onclick="qr(this)">{html.escape(failure.split("_")[-1])}</div>'
                for failure in qrbug.Failure['generate_qr'].children_ids
            ))
            texts.append('<p id="qr_code_gen_error_field"></p></p>')
            texts.append('<table>')
            texts.append('<tr><th> <th>Objet<th>')
            texts.append(html.escape(thing_comment.value))
            texts.append('<th colspan="2">Active<br>Finished<th>Pannes<th>Ajouter une panne</tr>')
            failure_del = qrbug.Failure['thing-del-failure']
            failure_add = qrbug.Failure['thing-add-failure']
            def go_in(node):
                texts.append('<tr><td>')
                texts.append(f'<input type="checkbox" class="qr_thing_checkboxes" id="qr_thing_checkbox_{node.id}" onclick="qr_select(this.checked, {repr(node.id)});" />')
                texts.append('<td>')
                texts.append(go_in.indent)
                texts.append(link_to_object('thing', node.id, request))
                texts.append('<td>')
                texts.append(qrbug.element(thing_comment, node, in_place=True))
                texts.append('<td>')
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
                    texts.append(qrbug.element(failure_del, node, destroy=failure_id))
                texts.append('<td>')
                texts.append(qrbug.element(failure_add, node, in_place=True, datalist_id="Failure"))
                texts.append('</tr>')
                go_in.indent += '    '
            def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
            datalists_to_load = ("Failure",)
        elif what is qrbug.Failure:
            failure_value = qrbug.Failure['failure-value']
            failure_ask_confirm = qrbug.Failure['failure-ask_confirm']
            failure_display = qrbug.Failure['failure-display_type']
            texts.append(VERT_STYLE)
            texts.append('''
            <table>
            <tr>
            <th>Panne
            <th>Intitulé
            <th>Confirmation
            <th class="vert">Affichage
            ''')
            def go_in(node):
                texts.append('<tr><td>')
                texts.append(go_in.indent)
                texts.append(link_to_object('failure', node.id, request))
                texts.append('<td>')
                texts.append(qrbug.element(failure_value, node, in_place=True))
                texts.append('<td>')
                texts.append(qrbug.element(failure_ask_confirm, node, in_place=True))
                texts.append('<td>')
                texts.append(qrbug.element(failure_display, node, in_place=True))
                texts.append('</tr>')
                go_in.indent += '    '
            def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
            datalists_to_load = tuple()
        elif what is qrbug.User:
            user_add_child = qrbug.Failure['user-add-child']
            user_del_child = qrbug.Failure['user-del-child']
            texts.append(VERT_STYLE)
            texts.append('''
            <style>

            </style>
            ''')
            texts.append('<table>')
            texts.append(
                f'<tr><th>ID<th class="vert">{user_del_child.value}<th>{user_add_child.value}</tr>'
            )
            parents: list["qrbug.UserId"] = []
            def go_in(user):
                parents.append(user.id)
                texts.append('<tr><td>')
                texts.append(go_in.indent)
                texts.append(html.escape(user.id))
                texts.append('<td>')
                has_parent = len(parents) >= 2
                if has_parent:
                    texts.append(qrbug.element(
                        user_del_child,
                        user,
                        in_place=True,
                        force_value='×',
                        destroy=parents[-2]
                    ))
                texts.append('<td>')
                texts.append(qrbug.element(
                    user_add_child, user, in_place=True, datalist_id='User'))
                texts.append('</tr>')
                go_in.indent += '        '
            def go_out(_node):
                go_in.indent = go_in.indent[:-8]
                parents.pop(-1)
            go_in.indent = ''
            footer = '</table>'
            datalists_to_load = ('User',)
        elif what is qrbug.Dispatcher:
            texts.append('<table>')
            texts.append(
                f'<tr><th>ID</th>'
                f'<th>{qrbug.Failure["dispatcher-selector_id"].value}</th>'
                f'<th>{qrbug.Failure["dispatcher-incidents"].value}</th>'
                f'<th>{qrbug.Failure["dispatcher-action_id"].value}</th></tr>'
            )
            def go_in(dispatcher):
                texts.append('<tr><td>')
                texts.append(html.escape(dispatcher.id))
                texts.append('</td><td>')
                texts.append(qrbug.element(qrbug.Failure['dispatcher-selector_id'], dispatcher, in_place=True, datalist_id='Selector'))
                texts.append('</td><td>')
                texts.append(qrbug.element(qrbug.Failure['dispatcher-incidents'], dispatcher, in_place=True, datalist_id='Selector'))
                texts.append('</td><td>')
                texts.append(qrbug.element(qrbug.Failure['dispatcher-action_id'], dispatcher, in_place=True, datalist_id='Action'))
                texts.append('</td></tr>')
            def go_out(_node):
                pass
            footer = '</table>'
            datalists_to_load = ('Selector', 'Action')
        else:
            def go_in(node):
                texts.append(html.escape(node.dump()))
                texts.append('<ul>')
            def go_out(_node):
                texts.append('</ul>')
            footer = ''
            datalists_to_load = tuple()
        for tree in what.roots():
            tree.walk(go_in, go_out, do_sort=True)
        texts.append(footer)
        texts = [qrbug.get_template(request, datalists_to_load).replace('%REPRESENTATION%', ''.join(texts))]
    elif what is qrbug.Action:
        action = qrbug.Failure['action-python_script']
        texts.append('<table>')
        texts.append('<tr><th>Action</th><th>')
        texts.append(html.escape(action.value))
        texts.append('</th></tr>')
        for node in sorted(what.instances.values(), key=lambda e: e.id):
            texts.append('<tr><td>')
            texts.append(link_to_object('action', node.id, request))
            texts.append('<td>')
            texts.append(qrbug.element(action, node, in_place=True, datalist_id='ActionScripts'))
            texts.append('</tr>')
        texts.append('</table>')
        texts = [qrbug.get_template(request, ("ActionScripts",)).replace('%REPRESENTATION%', ''.join(texts))]
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
    elif what is qrbug.Selector:
        texts.append(f'''
        <script>
        var LISTS = {{
            'Failure': {list(qrbug.Failure.instances)},
            'User': {list(qrbug.User.instances)},
            'Selector': {list(qrbug.Selector.instances)},
            'Thing': {list(qrbug.Thing.instances)}
            }};
        {qrbug.SELECTOR_SCRIPT_FUNCTIONS.read_text()}
        </script>
        <table><tr><th>ID<th><th><th><th>Concernés<th>Ajouter un concerné</tr><script>
        ''')
        selector_concerned_add = qrbug.Failure['selector-concerned-add']
        selector_concerned_del = qrbug.Failure['selector-concerned-del']
        for selector in sorted(what.instances.values(), key=lambda e: e.id):
            users = [
                f'{qrbug.element(selector_concerned_del, selector, destroy=user)}'
                for user in selector.concerned
                ]
            more = f'''
            <td>{' '.join(users)}
            <td>{qrbug.element(selector_concerned_add, selector, in_place=True, datalist_id="User")}
            '''
            texts.append('add_selector(')
            texts.append(json.dumps(selector.id))
            texts.append(',')
            texts.append(selector.expression)
            texts.append(',')
            texts.append(json.dumps(more))
            texts.append(');\n')
        texts.append('</script></table>')
        texts = [qrbug.get_template(request).replace('%REPRESENTATION%', ''.join(texts))]
    else:
        for node in what.instances.values() if hasattr(what, 'instances') else what.active:
            try:
                texts.append(html.escape(node.dump()) + '<br>')
            except: # pylint: disabled=bare-except
                texts.append(html.escape(str(node)) + '<br>')

    await request.write(''.join(texts))

    return None
