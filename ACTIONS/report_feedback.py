"""
Feedback on report
"""
import html

async def run(incidents, request):
    incident = incidents[0]
    if request.report.comment:
        comment = f'Vous avez précisé :<div>{html.escape(request.report.comment)}</div>'
    else:
        comment = ''
    await request.write(
        f"""
        <style>
        DIV {{ margin: 2em; font-weight: bold }}
        </style>
        Merci d'avoir signalé l'incident :
        <div>
        {html.escape(incident.failure.value)}
        </div>
        à propos de :
        <div>
        {html.escape(incident.thing_id)}
        </div>
        {comment}
        <p>Quelqu'un s'en occupera prochainement.""")
