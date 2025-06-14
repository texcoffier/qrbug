import html
from typing import Optional, List

import qrbug

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = [f'<h1>{incident.failure.value}</h1>']

    if issubclass(what, qrbug.Tree):
        if what is qrbug.Thing:
            thing_comment = qrbug.Failure['thing-comment']
            qr = 'QRCodes : ' + ' '.join(
                f'<button onclick="qr(this)">{html.escape(failure.split("_")[-1])}</button>'
                for failure in qrbug.Failure['generate_qr'].children_ids
            )
            texts.append('<table>')
            def go_in(node):
                texts.append('<tr><td>')
                texts.append(go_in.indent)
                texts.append('<a target="_blank" href="thing=')
                texts.append(html.escape(node.id))
                texts.append('">')
                texts.append(html.escape(node.id))
                texts.append('</a><td>')
                texts.append(qrbug.element(thing_comment, node, in_place=True))
                texts.append('<td>')
                texts.append(qr)
                texts.append('</tr>')
                go_in.indent += '    '
            def go_out(_node):
                go_in.indent = go_in.indent[:-4]
            go_in.indent = ''
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
        texts = [qrbug.get_template().replace('%REPRESENTATION%', ''.join(texts))]
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

    await request.write(''.join(texts))

    return None
