"""
Display data on browser
"""
from typing import Optional, List
from aiohttp import web

import qrbug

async def run(incidents: List[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    await request.response.write(b'Start\n')
    for incident in incidents:
        for report in incident.active:
            await request.response.write(
                f'{incident.thing_id},{incident.failure_id},{report.ip},{report.comment},{report.login},{report.remover_login}\n'
                .encode('utf-8'))
    await request.response.write(b'End\n')
