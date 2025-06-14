"""
Display data on browser
"""
import html
import urllib
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
            let iframe = document.createElement('IFRAME');
            iframe.src = element.getAttribute('url');
            iframe.style = "height:1.5em; width:1.5em; border:0px;vertical-align:middle";
            iframe.onload = function() { element.remove(); };
            element.insertAdjacentElement('afterend', iframe);
        }
        </script>
        <style>
        BODY { font-family: sans-serif }
        TABLE { border-spacing: 0px }
        TABLE, TABLE TD { border: 1px solid #DDD }
        TABLE TR.title { background: #F8F8F8 }
        TABLE TD { vertical-align: top; }
        </style><table>''')
    ticket = getattr(request, 'ticket', '')
    for incident in incidents:
        thing = urllib.parse.quote(incident.thing_id)
        failure = urllib.parse.quote(incident.failure_id)
        if incident.active:
            fix = f'''<button onclick="fix(this)"
            url="?what=thing&thing-id={thing}&failure-id={failure}&is-repaired=1&ticket={ticket}"
            >C'est réparé</button>'''
        elif incident.pending_feedback:
            fix = f'''<button onclick="fix(this)"
            url="?what=thing&thing-id={thing}&failure-id={failure}&is-repaired=1&ticket={ticket}"
            >Prévenir les utilisateurs que c'est réparé</button>
            '''
        else:
            fix = 'BUG'
        await request.write(
            f'''<tr class="title">
            <td rowspan="{len(incident.active)+len(incident.pending_feedback)+1}">«{escape(incident.thing_id)}»<br>«{escape(incident.failure_id)}»<br>
            {fix}<td>IP demandeur<td>Commentaire<td>Qui a demandé<td>Réparateur</tr>\n''')
        for report in incident.active:
            await request.write(
                f'<tr><td>{escape(report.ip)}<td>{escape(report.comment)}<td>{escape(report.login)}</tr>'
            )
        for report in incident.pending_feedback:
            await request.write(
                f'<tr><td>{escape(report.ip)}<td>{escape(report.comment)}<td>{escape(report.login)}<td>{escape(report.remover_login)}</tr>'
            )
    await request.write('</table>\n')
