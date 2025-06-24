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
        email = await qrbug.get_mail_from_login(user)
        await request.write(f'<p>{email} ({user}) {message}\n')
        await qrbug.send_mail(
            email,
            f"QRBUG : {len(incidents)} pannes ont été réparées",
            body,
            show_to=True)
    await request.write("<p>C'est fini.\n")
    qrbug.Incident.pending_feedback = {} # Only for unittests
