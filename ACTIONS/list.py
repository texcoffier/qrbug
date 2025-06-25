import html
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

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = [f'<title>{incident.failure.value}</title><h1>{incident.failure.value}</h1>']

    if issubclass(what, qrbug.Tree):
        if what is qrbug.Thing:
            thing_comment = qrbug.Failure['thing-comment']
            texts.append('<p>Générer une feuille de QR codes (lignes × colonne) : ')
            texts.append(' '.join(
                f'<button onclick="qr(this)">{html.escape(failure.split("_")[-1])}</button>'
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
            failure_allowed = qrbug.Failure['failure-allowed']
            texts.append('''
            <style>
            .vert { writing-mode: sideways-lr; font-weight: normal; font-size: 60%; }
            </style>
            <table>
            <tr>
            <th>Panne
            <th>Intitulé
            <th class="vert">Confirmation
            <th class="vert">Affichage
            <th>Déclaration autorisée<br>si la condition est vraie</tr>''')
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
                texts.append('<td>')
                texts.append(qrbug.element(failure_allowed, node, in_place=True))
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
            user_add_parent = qrbug.Failure['user-add-parent']
            user_del_parent = qrbug.Failure['user-del-parent']
            texts.append('<div class="button" onclick="location.reload()">RAFRAÎCHIR</div>')
            texts.append('<table>')
            texts.append(
                f'<tr><th>ID<th>{user_add_child.value}<th>{user_del_child.value}'
                f'<th>{user_add_parent.value}<th>{user_del_parent.value}</tr>'
            )
            def go_in(user):
                texts.append('<tr><td>')
                texts.append(go_in.indent)
                texts.append(html.escape(user.id))
                texts.append('<td>')
                texts.append(qrbug.element(user_add_child, user, in_place=True, datalist_id='User'))
                texts.append('<td>')
                texts.append(qrbug.element(user_del_child, user, in_place=True, datalist_id='User'))
                texts.append('<td>')
                texts.append(qrbug.element(user_add_parent, user, in_place=True, datalist_id='User'))
                texts.append('<td>')
                texts.append(qrbug.element(user_del_parent, user, in_place=True, datalist_id='User'))
                texts.append('</tr>')
                go_in.indent += '    '
            def go_out(_node):
                go_in.indent = go_in.indent[:-4]
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
    elif issubclass(what, qrbug.Concerned):
        texts.append('<table border>')
        concerned_add = qrbug.Failure['concerned-add']
        concerned_del = qrbug.Failure['concerned-del']
        texts.append(f'''<tr>
            <th>Le selecteur d'incident
            <th>Personne/groupe concernés
            <th>{html.escape(concerned_add.value)}
            </tr>''')
        for selector_id, concerned in sorted(what.instances.items(), key=lambda e: e[0]):
            users = [
                f'{qrbug.element(concerned_del, concerned, destroy=user)}'
                for user in concerned.users
                ]
            texts.append(f'''<tr>
            <td><a href="selector={selector_id}?secret={request.secret.secret}">{html.escape(selector_id)}</a>
            <td>{' '.join(users)}
            <td>{qrbug.element(concerned_add, concerned, in_place=True, datalist_id="User")}
            </tr>''')
        texts.append('</table>')
        texts = [qrbug.get_template(request, ("User",)).replace('%REPRESENTATION%', ''.join(texts))]
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
        texts.append('<table>')
        texts.append('<tr><th>ID</th><th>Expression</th></tr>')
        for selector in sorted(what.instances.values(), key=lambda e: e.id):
            texts.append('<tr><td>')
            texts.append(html.escape(selector.id))
            texts.append('</td><td>')
            texts.append(qrbug.element(qrbug.Failure['selector-expression'], selector, in_place=True))
            # texts.append(html.escape(selector.expression))
            texts.append('</td></tr>')
        texts = [qrbug.get_template(request).replace('%REPRESENTATION%', ''.join(texts))]
    else:
        for node in what.instances.values() if hasattr(what, 'instances') else what.active:
            try:
                texts.append(html.escape(node.dump()) + '<br>')
            except: # pylint: disabled=bare-except
                texts.append(html.escape(str(node)) + '<br>')

    await request.write(''.join(texts))

    return None
