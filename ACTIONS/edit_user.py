"""
In this case, the thing is a user ID to edit
"""
import html

import qrbug


CHECK_VALID_LOGIN = False


async def run(incidents, request):  # TODO: Force refresh of the page upon edit
    incident = incidents[0]
    user_id = incident.thing_id
    value = request.report.comment
    feedback = ''
    if incident.failure_id == 'user-add-child':
        error_message = qrbug.User[user_id].can_add_child(value)
        if error_message:
            feedback = f"<b>ERREUR :</b> {error_message}"
        else:
            if value not in qrbug.User.instances.keys():  # If the user doesn't exist, we create it !
                if not CHECK_VALID_LOGIN or ((await qrbug.get_mail_from_login(value)) != qrbug.DEFAULT_EMAIL_TO):  # If the user has a valid email
                    qrbug.append_line_to_journal(f'user_update({repr(value)})\n', qrbug.Journals.DB)
                else:
                    feedback = f"<b>ERREUR :</b> L'utilisateur «{html.escape(value)}» n'a pas d'adresse mail valide, et ne sera donc pas créé."
            if not feedback:
                qrbug.append_line_to_journal(f'user_add({repr(user_id)}, {repr(value)})\n', qrbug.Journals.DB)
                feedback = f"Ajouté l'enfant «{html.escape(value)}» à «{user_id}»\n"
    elif incident.failure_id == 'user-del-child':
        error_message = qrbug.User[value].can_remove_child(user_id)
        if error_message:
            feedback = f"<b>ERREUR :</b> {error_message}"
        else:
            qrbug.append_line_to_journal(f'user_remove({repr(value)}, {repr(user_id)})\n', qrbug.Journals.DB)
            feedback = f"Retiré l'enfant «{user_id}» à «{html.escape(value)}»\n"
    else:
        feedback = "Unexpected edit failure for User\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
