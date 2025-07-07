"""
Take all incidents, get concerned users and send one resume mail per user.
"""

import asyncio
import collections
import html
import qrbug


async def run(incidents: list[qrbug.Incident], request: qrbug.Request) -> None:
    incidents_per_user = collections.defaultdict(list)
    for concerned_id, concerned in tuple(qrbug.Concerned.instances.items()):
        for incident in incidents:
            if qrbug.Selector[concerned_id].is_ok(request.incident, request.report, incident):
                for user in concerned.users:
                    for child in qrbug.User[user].get_all_children_ids():
                        incidents_per_user[child].append(
                            (qrbug.Thing[incident.thing_id].path(), incident.failure_id, incident)
                            )
        await asyncio.sleep(0)

    for user, incidents in incidents_per_user.items():
        incidents.sort()
        message = [
            '<html>',
            'Voici les incidents actuellement actifs pour lesquels vous êtes concerné'
            ]
        last_path = ''
        for path, failure_id, incident in incidents:
            if path != last_path:
                if last_path:
                    message.append('</ul>')
                message.append(f'<p><a href="{qrbug.SERVICE_URL}/thing={html.escape(incident.thing_id)}">{path}</a><ul>')
                last_path = path
            message.append(f'<li> «{html.escape(failure_id)}» : «{html.escape(incident.failure.value)}» {len(incident.active)} rapports')
        if last_path:
            message.append('</ul>')
        message.append('</html>')
        email = await qrbug.get_mail_from_login(user)
        await qrbug.send_mail(
            email,
            "QRBUG : vos incidents actifs",
            '\n'.join(message),
            show_to=True)
        await request.write(f'<p>Envoit un mail à {email} ({user}) à propos de {len(incidents)} incidents')
    await request.write("<p>C'est fini")

