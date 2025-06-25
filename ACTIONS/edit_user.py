"""
In this case, the thing is a user ID to edit
"""
import html

import qrbug

async def run(incidents, request):
    incident = incidents[0]
    user_id = incident.thing_id
    value = html.escape(request.report.comment)
    if incident.failure_id == 'user-add-child':
        qrbug.append_line_to_journal(f'user_add({repr(user_id)}, {repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Ajouté l'enfant «{value}» à «{user_id}»\n"
    elif incident.failure_id == 'user-del-child':
        qrbug.append_line_to_journal(f'user_remove({repr(user_id)}, {repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Retiré l'enfant «{value}» à «{user_id}»\n"  # TODO: Error handling
    else:
        feedback = "Unexpected edit failure for User\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
