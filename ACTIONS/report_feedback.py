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
        <title>Rapport {html.escape(incident.thing_id)} {html.escape(incident.failure_id)}</title>
        Merci d'avoir signalé l'incident :
        <div>
        {html.escape(incident.failure.name('¤')).replace('¤', '<br>')}
        </div>
        à propos de :
        <div>
        {html.escape(incident.thing.name('¤')).replace('¤', '<br>')}
        </div>
        {comment}
        <p>Quelqu'un s'en occupera prochainement.""")
