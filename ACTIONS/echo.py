"""
Display data on browser
"""
from typing import Optional, List
from aiohttp import web

import qrbug

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    await request.response.write(b'<pre>\n')
    for incident in incidents:
        for report in incident.active:
            await request.response.write(
                f'Active {incident.thing_id},{incident.failure_id},{report.ip},{report.comment},{report.login},{report.remover_login}\n'
                .encode('utf-8'))
        for report in incident.pending_feedback:
            await request.response.write(
                f'Pending feedback {incident.thing_id},{incident.failure_id},{report.ip},{report.comment},{report.login},{report.remover_login}\n'
                .encode('utf-8'))
    await request.response.write(b'</pre>\n')
