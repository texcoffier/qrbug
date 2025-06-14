"""
In this case, the thing is a thing ID to edit
"""
import html
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'thing-comment':
        qrbug.append_line_to_journal(
                f'thing_update({repr(selector)}, comment={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le commentaire est maintenant «{html.escape(value)}»\n"
    else:
        feedback = "Unexpected edit failure for Thing\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
