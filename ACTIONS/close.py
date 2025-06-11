"""
Display data on browser
"""
from typing import Optional, List

import qrbug

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    for incident in incidents:
        await request.write(
            f'«Clôture de {incident.failure.path()}» «{incident.failure.value}»\n'
        )
        incident.incident_del()
