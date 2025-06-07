"""
Close the incident.
It is for the backoffice API.
"""
async def run(incidents, _request):
    for incident in incidents:
        incident.incident_del()
