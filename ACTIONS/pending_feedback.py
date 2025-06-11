"""
Display data on browser


await qrbug.send_mail(
    qrbug.get_user_from_login(report.login),
    'Incident réparé',
    f'Merci d\'avoir signalé l\'incident {repr(failure.value)} sur {repr(thing_id)} !\nCet incident vient tout juste d\'être résolu !'
)

"""
from typing import Optional, List
from aiohttp import web

import qrbug

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    await request.response.write(b'<pre>\n')
    # Fusion messages in one mail per user
    for incident in incidents:
        for report in incident.pending_feedback:
            await request.response.write(
                f'SEND FEEDBACK FOR {incident.thing_id},{incident.failure_id},{report.ip},{report.comment},{report.login},{report.remover_login}\n'
                .encode('utf-8'))
        incident.pending_feedback = []
    await request.response.write(b'</pre>\n')
