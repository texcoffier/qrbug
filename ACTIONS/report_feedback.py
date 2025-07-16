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
        f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
    <link REL="icon" HREF="favicon.ico">
    <style>
        BODY {{ font-family: sans-serif }}
        DIV {{ margin: 2em; font-weight: bold; white-space: pre }}
        @media (orientation: portrait) {{ BODY {{ font-size: 5vw }} }}
   </style>
</head>
<body>
    <title>Rapport {html.escape(incident.thing_id)} {html.escape(incident.failure_id)}</title>
    Merci d'avoir signalé l'incident :
    <div>{html.escape(incident.failure.name('¤')).replace('¤', '<br>')}</div>
    à propos de :
    <div>{html.escape(incident.thing.name('¤')).replace('¤', '<br>')}</div>
    {comment}
    <p>Quelqu'un s'en occupera prochainement.""")
