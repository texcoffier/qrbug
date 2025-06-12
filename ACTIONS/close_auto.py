"""
Close the incident.
It is for the backoffice API.

Pending feedback is cleared on 'send-pending-feedback' failure dispatch
"""
async def run(incidents, _request):
    for incident in incidents:
        incident.incident_del()
