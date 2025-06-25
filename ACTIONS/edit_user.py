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
        if value == user_id:
            feedback = f"<b>ERREUR :</b> Impossible d'assigner le même ID à un parent et un enfant"
        elif value in qrbug.User[user_id].get_all_children_ids():
            feedback = f"<b>ERREUR :</b> «{value}» est déjà un enfant de «{user_id}»"
        else:
            qrbug.append_line_to_journal(f'user_add({repr(user_id)}, {repr(value)})\n', qrbug.Journals.DB)
            feedback = f"Ajouté l'enfant «{value}» à «{user_id}»\n"
    elif incident.failure_id == 'user-del-child':
        if value == user_id:
            feedback = f"<b>ERREUR :</b> L'ID du parent est identique à celui de l'enfant"
        elif value not in qrbug.User[user_id].children_ids:
            feedback = f"<b>ERREUR :</b> «{value}» n'est pas un enfant de «{user_id}»"
        else:
            qrbug.append_line_to_journal(f'user_remove({repr(user_id)}, {repr(value)})\n', qrbug.Journals.DB)
            feedback = f"Retiré l'enfant «{value}» à «{user_id}»\n"
    else:
        feedback = "Unexpected edit failure for User\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
