"""
Display data on browser
"""
from typing import Optional, List
from aiohttp import web

import qrbug

async def run(incidents: List[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    for incident in incidents:
        await request.response.write(
        f'«Clôture de {incident.failure.path()}» «{incident.failure.value}»\n'
        .encode('utf-8'))
        incident.incident_del()
