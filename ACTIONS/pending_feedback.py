"""
Send fix feedback to users.
"""
import collections
import html
from typing import Optional, List

import qrbug

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    await request.write('Les feedback de réparation ont été envoyés pour :\n')
    incidents_per_user = collections.defaultdict(list)
    for (thing_id, failure_id), reports in qrbug.Incident.pending_feedback.items():
        for report in reports:
            if report.login:
                incidents_per_user[report.login].append((thing_id, failure_id))

    for user, incidents in incidents_per_user.items():
        message = ['<ul>']
        for thing_id, failure_id in sorted(incidents):
            message.append(
                f'<li> {html.escape(qrbug.Thing[thing_id].name())} : {html.escape(qrbug.Failure[failure_id].name())}')
        message.append('</ul>')
        message = ''.join(message)
        body = f'''<html><p>Bonjour {user}.
<p>
Les incidents suivants que vous avez déclaré ont été réparés :
{message}

Ceci est un message automatique.
</html>
'''
        await request.write(f'<p>{user}{message}\n')
        try:
            await qrbug.send_mail(
            user,
            f"QRBUG : {len(incidents)} pannes ont été réparées",
            body,
            show_to=True)
        except ValueError:
            await request.write(
                '<p style="background:#F88"><p>L\'envoie du message précédent a échoué.\n')
    await request.write("<p>C'est fini.\n")
    qrbug.Incident.pending_feedback = {} # Only for unittests
