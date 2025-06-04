import html
from typing import Optional, List
from aiohttp import web

import qrbug

async def run(incidents: List[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    await request.response.write(f'<h1>{qrbug.Failure[incident.failure_id].value}</h1>'
        .encode('utf-8'))

    what = getattr(qrbug, incident.failure_id.split('-')[1])
    texts = []

    if issubclass(what, qrbug.Tree):
        def go_in(node):
            texts.append(html.escape(node.dump()))
            texts.append('<ul>')
        def go_out(node):
            texts.append('</ul>')
        for tree in what.roots():
            tree.walk(go_in, go_out)
    else:
        for node in what.instances.values() if hasattr(what, 'instances') else what.active:
            try:
                texts.append(html.escape(node.dump()) + '<br>')
            except:
                texts.append(html.escape(str(node)) + '<br>')

    await request.response.write(''.join(texts).encode('utf-8'))
    incident.incident_del()

    return None
