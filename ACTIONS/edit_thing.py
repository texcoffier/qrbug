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
    elif incident.failure_id == 'thing-del-failure':
        if value in incident.thing.failure_ids:
            qrbug.append_line_to_journal(
                f'thing_del_failure({repr(selector)}, {repr(value)})\n', qrbug.Journals.DB)
            feedback = f"La panne «{html.escape(value)}» a été enlevée.\n"
        else:
            feedback = "La panne n'était pas présente"
    elif incident.failure_id == 'thing-add-failure':
        if value in qrbug.Failure.instances:
            qrbug.append_line_to_journal(
                f'thing_add_failure({repr(selector)}, {repr(value)})\n', qrbug.Journals.DB)
            feedback = f"La panne «{html.escape(value)}» a été ajoutée.\n"
        else:
            feedback = "Cette panne n'existe pas"
    else:
        feedback = "Unexpected edit failure for Thing\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
