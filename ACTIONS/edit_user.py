"""
In this case, the thing is a user ID to edit
"""
import html

import qrbug

async def run(incidents, request):  # TODO: Force refresh of the page upon edit
    incident = incidents[0]
    user_id = incident.thing_id
    value = html.escape(request.report.comment)
    if incident.failure_id == 'user-add-child':
        can_add_child, message = qrbug.User[user_id].can_add_child(value)
        if not can_add_child:
            feedback = f"<b>ERREUR :</b> {message}"
        else:
            qrbug.append_line_to_journal(f'user_add({repr(user_id)}, {repr(value)})\n', qrbug.Journals.DB)
            feedback = f"Ajouté l'enfant «{value}» à «{user_id}»\n"
    elif incident.failure_id == 'user-del-child':
        can_remove_child, message = qrbug.User[value].can_remove_child(user_id)
        if not can_remove_child:
            feedback = f"<b>ERREUR :</b> {message}"
        else:
            qrbug.append_line_to_journal(f'user_remove({repr(value)}, {repr(user_id)})\n', qrbug.Journals.DB)
            feedback = f"Retiré l'enfant «{user_id}» à «{value}»\n"
    else:
        feedback = "Unexpected edit failure for User\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
