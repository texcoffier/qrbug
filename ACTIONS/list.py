import html
from typing import Optional, List

import qrbug

def link_to_object(what, thing_id, label=None):
    thing_id = html.escape(thing_id)
    if label is None:
        label = thing_id
    return f'<a target="_blank" href="{what}={thing_id}">{label}</a>'

def link_to_active(thing_id):
    active = sum(len(i.active) for i in qrbug.Incident.instances[thing_id].values())
    if not active:
        return ''
    return f'<a target="_blank" href="?failure-id=thing-incidents-active&thing-id={thing_id}">{active}</a>'

def link_to_finished(thing_id):
    finished = sum(len(i.finished) for i in qrbug.Incident.instances[thing_id].values())
    if not finished:
        return ''
    return f'<a target="_blank" href="?failure-id=thing-incidents&thing-id={thing_id}">{finished}</a>'

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = [f'<title>{incident.failure.value}</title><h1>{incident.failure.value}</h1>']

    if issubclass(what, qrbug.Tree):
        if what is qrbug.Thing:
            thing_comment = qrbug.Failure['thing-comment']
            texts.append(f'<p>Générer une feuille de QR codes : ')
            texts.append(' '.join(
                f'<button onclick="qr(this)">{html.escape(failure.split("_")[-1])}</button>'
                for failure in qrbug.Failure['generate_qr'].children_ids
            ))
            texts.append(f'<p id="qr_code_gen_error_field"></p></p>')
            texts.append('<table>')
            texts.append('<tr><th> <th>Objet<th>')
            texts.append(html.escape(thing_comment.value))
            texts.append('<th colspan="2">Active<br>Finished</tr>')
            def go_in(node):
                texts.append('<tr><td>')
                texts.append(f'<input type="checkbox" class="qr_thing_checkboxes" id="qr_thing_checkbox_{node.id}" onclick="qr_select(this.checked, {repr(node.id)});" />')
                texts.append('<td>')
                texts.append(go_in.indent)
                texts.append(link_to_object('thing', node.id))
                texts.append('<td>')
                texts.append(qrbug.element(thing_comment, node, in_place=True))
                texts.append('<td>')
                thing_incident = qrbug.Incident.instances.get(node.id, None)
                if thing_incident:
                    texts.append(link_to_active(node.id))
                    texts.append('<td>')
                    texts.append(link_to_finished(node.id))
                else:
                    texts.append('<td>')
                texts.append('</tr>')
                go_in.indent += '    '
            def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
        elif what is qrbug.Failure:
            failure_value = qrbug.Failure['failure-value']
            failure_ask_confirm = qrbug.Failure['failure-ask_confirm']
            failure_display = qrbug.Failure['failure-display_type']
            failure_allowed = qrbug.Failure['failure-allowed']
            texts.append('<table>')
            texts.append('<tr><th>Panne<th>Intitulé<th>Confirmation<th>Affichage<th>Autorisé pour</tr>')
            def go_in(node):
                texts.append('<tr><td>')
                texts.append(go_in.indent)
                texts.append(link_to_object('failure', node.id))
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
        elif what is qrbug.User:
            texts.append('<table>')
            texts.append('<tr><th>ID</th></tr>')
            def go_in(user):
                texts.append('<tr><td>')
                texts.append(go_in.indent)
                texts.append(html.escape(user.id))
                texts.append('</td></tr>')
                go_in.indent += '    '
            def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
        elif what is qrbug.Dispatcher:
            texts.append('<table>')
            texts.append(
                f'<tr><th>ID</th>'
                f'<th>{qrbug.Failure["dispatcher-action_id"].value}</th>'
                f'<th>{qrbug.Failure["dispatcher-selector_id"].value}</th></tr>'
            )
            def go_in(dispatcher):
                texts.append('<tr><td>')
                texts.append(html.escape(dispatcher.id))
                texts.append('</td><td>')
                texts.append(qrbug.element(qrbug.Failure['dispatcher-action_id'], dispatcher, in_place=True))
                texts.append('</td><td>')
                texts.append(qrbug.element(qrbug.Failure['dispatcher-selector_id'], dispatcher, in_place=True))
                texts.append('</td></tr>')
            def go_out(_node):
                pass
            footer = '</table>'
        else:
            def go_in(node):
                texts.append(html.escape(node.dump()))
                texts.append('<ul>')
            def go_out(_node):
                texts.append('</ul>')
            footer = ''
        for tree in what.roots():
            tree.walk(go_in, go_out)
        texts.append(footer)
        texts = [qrbug.get_template(request).replace('%REPRESENTATION%', ''.join(texts))]
    elif issubclass(what, qrbug.Concerned):
        texts.append('<table border>')
        concerned_add = qrbug.Failure['concerned-add']
        concerned_del = qrbug.Failure['concerned-del']
        texts.append(f'''<tr>
            <th>Le selecteur d'incident
            <th>Personne/groupe concernés
            <th>{html.escape(concerned_add.value)}
            <th>{html.escape(concerned_del.value)}
            </tr>''')
        for selector_id, concerned in what.instances.items():
            users = [
                f'<a href="user={user}?secret={request.secret.secret}">{html.escape(user)}</a>'
                for user in concerned.users
                ]
            texts.append(f'''<tr>
            <td><a href="selector={selector_id}?secret={request.secret.secret}">{html.escape(selector_id)}</a>
            <td>{' '.join(users)}
            <td>{qrbug.element(concerned_add, concerned, in_place=True)}
            <td>{qrbug.element(concerned_del, concerned, in_place=True)}
            </tr>''')
        texts.append('</table>')
        texts = [qrbug.get_template(request).replace('%REPRESENTATION%', ''.join(texts))]
    elif what is qrbug.Action:
        action = qrbug.Failure['action-python_script']
        texts.append('<table>')
        texts.append('<tr><th>Action</th><th>')
        texts.append(html.escape(action.value))
        texts.append('</th></tr>')
        for node in what.instances.values():
            texts.append('<tr><td>')
            texts.append(link_to_object('action', node.id))
            texts.append('<td>')
            texts.append(qrbug.element(action, node, in_place=True))
            texts.append('</tr>')
        texts.append('</table>')
        texts = [qrbug.get_template(request).replace('%REPRESENTATION%', ''.join(texts))]
    elif what is qrbug.Incident:
        texts.append('<table border><tr><th>Objet<th>Actives<th>Réparés<th>Panne<th>Active<th>Réparées')
        for thing_id, failures in sorted(what.instances.items()):
            texts.append(f'''<tr><td rowspan="{len(failures)}">
            {link_to_object("thing", thing_id)}
            <td rowspan="{len(failures)}">{link_to_active(thing_id)}
            <td rowspan="{len(failures)}">{link_to_finished(thing_id) or "0"}''')
            prefix = ''
            for failure_id, failure in failures.items():
                texts.append(f'''{prefix}<td>{link_to_object("failure", failure_id)}
                <td>{len(failure.active)}
                <td>{len(failure.finished)}
                </tr>
                ''')
        texts.append('</table>')
    elif what is qrbug.Selector:
        texts.append('<table>')
        texts.append('<tr><th>ID</th><th>Expression</th></tr>')
        for selector in what.instances.values():
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
