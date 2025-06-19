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
    await request.write(f'<style>{qrbug.BASE_STYLE_TEMPLATE.read_text()}</style>')
    await request.write(f'<title>{incident.failure.value}</title><h1>{incident.failure.value}</h1>')

    if issubclass(what, qrbug.Tree):
        if what is qrbug.Thing:
            thing_comment = qrbug.Failure['thing-comment']
            await request.write(f'<p>Générer une feuille de QR codes : ')
            await request.write(' '.join(
                f'<button onclick="qr(this)">{html.escape(failure.split("_")[-1])}</button>'
                for failure in qrbug.Failure['generate_qr'].children_ids
            ))
            await request.write(f'<p id="qr_code_gen_error_field"></p></p>')
            await request.write('<table>')
            await request.write('<tr><th>Objet<th>')
            await request.write(html.escape(thing_comment.value))
            await request.write('<th>En faire un QR code<th colspan="2">Active<br>Finished</tr>')
            async def go_in(node):
                await request.write('<tr><td>')
                await request.write(go_in.indent)
                await request.write(link_to_object('thing', node.id))
                await request.write('<td>')
                await request.write(qrbug.element(thing_comment, node, in_place=True))
                await request.write('<td>')
                await request.write(f'<input type="checkbox" onclick="qr_select(this.checked, {repr(node.id)});" />')
                await request.write('<td>')
                thing_incident = qrbug.Incident.instances.get(node.id, None)
                if thing_incident:
                    await request.write(link_to_active(node.id))
                    await request.write('<td>')
                    await request.write(link_to_finished(node.id))
                else:
                    await request.write('<td>')
                await request.write('</tr>')
                go_in.indent += '    '
            async def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
        elif what is qrbug.Failure:
            failure_value = qrbug.Failure['failure-value']
            failure_ask_confirm = qrbug.Failure['failure-ask_confirm']
            failure_display = qrbug.Failure['failure-display_type']
            failure_allowed = qrbug.Failure['failure-allowed']
            await request.write('<table>')
            await request.write('<tr><th>Panne<th>Intitulé<th>Confirmation<th>Affichage<th>Autorisé pour</tr>')
            async def go_in(node):
                await request.write('<tr><td>')
                await request.write(go_in.indent)
                await request.write(link_to_object('failure', node.id))
                await request.write('<td>')
                await request.write(qrbug.element(failure_value, node, in_place=True))
                await request.write('<td>')
                await request.write(qrbug.element(failure_ask_confirm, node, in_place=True))
                await request.write('<td>')
                await request.write(qrbug.element(failure_display, node, in_place=True))
                await request.write('<td>')
                await request.write(qrbug.element(failure_allowed, node, in_place=True))
                await request.write('</tr>')
                go_in.indent += '    '
            async def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
        elif what is qrbug.User:
            await request.write('<table>')
            await request.write('<tr><th>ID</th></tr>')
            async def go_in(user):
                await request.write('<tr><td>')
                await request.write(go_in.indent)
                await request.write(html.escape(user.id))
                await request.write('</td></tr>')
                go_in.indent += '    '
            async def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
            footer = '</table>'
        else:
            async def go_in(node):
                await request.write(html.escape(node.dump()))
                await request.write('<ul>')
            async def go_out(_node):
                await request.write('</ul>')
            footer = ''
        for tree in what.roots():
            await tree.walk_async(go_in, go_out)
        await request.write(footer)
    elif issubclass(what, qrbug.Concerned):
        await request.write('<table border>')
        concerned_add = qrbug.Failure['concerned-add']
        concerned_del = qrbug.Failure['concerned-del']
        await request.write(f'''<tr>
            <th>Le selecteur d'incident
            <th>Personne/groupe concernés
            <th>{html.escape(concerned_add.value)}
            <th>{html.escape(concerned_del.value)}
            </tr>''')
        for selector_id, concerned in what.instances.items():
            users = [
                f'<a href="user={user}?ticket={request.ticket}">{html.escape(user)}</a>'
                for user in concerned.users
                ]
            await request.write(f'''<tr>
            <td><a href="selector={selector_id}?ticket={request.ticket}">{html.escape(selector_id)}</a>
            <td>{' '.join(users)}
            <td>{qrbug.element(concerned_add, concerned, in_place=True)}
            <td>{qrbug.element(concerned_del, concerned, in_place=True)}
            </tr>''')
        await request.write('</table>')
    elif what is qrbug.Action:
        action = qrbug.Failure['action-python_script']
        await request.write('<table>')
        await request.write('<tr><th>Action</th><th>')
        await request.write(html.escape(action.value))
        await request.write('</th></tr>')
        for node in what.instances.values():
            await request.write('<tr><td>')
            await request.write(link_to_object('action', node.id))
            await request.write('<td>')
            await request.write(qrbug.element(action, node, in_place=True))
            await request.write('</tr>')
        await request.write('</table>')
    elif what is qrbug.Incident:
        await request.write('<table border><tr><th>Objet<th>Actives<th>Réparés<th>Panne<th>Active<th>Réparées')
        for thing_id, failures in sorted(what.instances.items()):
            await request.write(f'''<tr><td rowspan="{len(failures)}">
            {link_to_object("thing", thing_id)}
            <td rowspan="{len(failures)}">{link_to_active(thing_id)}
            <td rowspan="{len(failures)}">{link_to_finished(thing_id) or "0"}''')
            prefix = ''
            for failure_id, failure in failures.items():
                await request.write(f'''{prefix}<td>{link_to_object("failure", failure_id)}
                <td>{len(failure.active)}
                <td>{len(failure.finished)}
                </tr>
                ''')
        await request.write('</table>')
    elif what is qrbug.Selector:
        await request.write('<table>')
        await request.write('<tr><th>ID</th><th>Expression</th></tr>')
        for selector in what.instances.values():
            await request.write('<tr><td>')
            await request.write(html.escape(selector.id))
            await request.write('</td><td>')
            await request.write(html.escape(selector.expression))
            await request.write('</td></tr>')
    else:
        for node in what.instances.values() if hasattr(what, 'instances') else what.active:
            try:
                await request.write(html.escape(node.dump()) + '<br>')
            except: # pylint: disabled=bare-except
                await request.write(html.escape(str(node)) + '<br>')

    return None
