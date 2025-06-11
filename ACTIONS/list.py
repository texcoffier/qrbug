import html
from typing import Optional, List

import qrbug

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = [f'<h1>{incident.failure.value}</h1>']

    if issubclass(what, qrbug.Tree):
        def go_in(node):
            texts.append(html.escape(node.dump()))
            texts.append('<ul>')
        def go_out(_node):
            texts.append('</ul>')
        for tree in what.roots():
            tree.walk(go_in, go_out)
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
                f'<a href="user={user}?ticket={request.ticket}">{html.escape(user)}</a>'
                for user in concerned.users
                ]
            texts.append(f'''<tr>
            <td><a href="selector={selector_id}?ticket={request.ticket}">{html.escape(selector_id)}</a>
            <td>{' '.join(users)}
            <td>{qrbug.element(concerned_add, concerned, in_place=True)}
            <td>{qrbug.element(concerned_del, concerned, in_place=True)}
            </tr>''')
        texts.append('</table>')
        texts = [qrbug.get_template().replace('%REPRESENTATION%', ''.join(texts))]
    else:
        for node in what.instances.values() if hasattr(what, 'instances') else what.active:
            try:
                texts.append(html.escape(node.dump()) + '<br>')
            except: # pylint: disabled=bare-except
                texts.append(html.escape(str(node)) + '<br>')

    await request.response.write(''.join(texts).encode('utf-8'))

    return None
