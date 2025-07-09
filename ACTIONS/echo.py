"""
Display data on browser
"""
import html
import urllib
import time
from typing import Optional, List

import qrbug

def escape(x):
    if x is None:
        return 'None'
    if x == '':
        return ' '
    return html.escape(x)

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    await request.write('''
        <script>
        function fix(element) {
            let iframe = element.nextSibling;
            iframe.contentWindow.location.replace(element.getAttribute('url'));
            iframe.onload = function() { element.remove(); };
        }
        </script>
        <style>
        BODY { font-family: sans-serif }
        TABLE { border-spacing: 0px }
        TABLE, TABLE TD { border: 1px solid #DDD }
        TABLE TR.title { background: #F8F8F8 }
        TABLE TD { vertical-align: top; }
        IFRAME { height:1.5em; width:1.5em; border:0px; vertical-align:middle }
        </style>
        <title>Incidents %s</title>
        <h1>Liste d'incidents (%s)</h1>
        <table>''' % (request.incident.failure_id, request.incident.failure_id))
    for incident in incidents:
        thing = urllib.parse.quote(incident.thing_id)
        failure = urllib.parse.quote(incident.failure_id)
        pending_feedbacks = incident.pending_feedback.get((incident.thing_id, incident.failure_id), ())
        if incident.active:
            fix = f'''<button onclick="fix(this)"
            url="?thing-id={thing}&failure-id={failure}&is-repaired=1&secret={request.secret.secret}"
            >C'est réparé</button><iframe></iframe>'''
        elif pending_feedbacks:
            fix = 'Utilisateur non prévenu'
        else:
            fix = ''

        await request.write(
            f'''<tr class="title">
            <td rowspan="{len(incident.active)+len(pending_feedbacks)+1}">«{escape(incident.thing_id)}»<br>«{escape(incident.failure_id)}»<br>
            {fix}<td>IP demandeur<td>Quand<td>Commentaire<td>Qui a demandé<td>Réparateur</tr>\n''')
        for report in (*incident.active, *pending_feedbacks):
            comment = escape(report.comment).replace("\n", "<br>").replace(' ', ' ')
            reporter = escape(report.login) if report.login else ''
            remover = escape(report.remover_login) if report.remover_login else ''
            ip = escape(report.ip)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp))
            await request.write(
                f'<tr><td>{ip}<td>{date}<td>{comment}<td>{reporter}<td>{remover}</tr>'
            )
    await request.write('</table>\n')
