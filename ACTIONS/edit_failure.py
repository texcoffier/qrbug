"""
In this case, the thing is a failure ID to edit
"""
import ast
import html

import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = request.report.comment
    feedback = f"La valeur de «{selector} . {incident.failure_id}» est inchangé.\n"
    failure = qrbug.Failure[selector]
    if incident.failure_id == 'failure-value':
        if value != failure.value:
            request.update_configuration(
                    f'failure_update({repr(selector)}, value={repr(value)})')
            feedback = f"Le titre de la panne «{selector}» est maintenant «{html.escape(value)}»\n"
    elif incident.failure_id == 'failure-display_type':
        try:
            if qrbug.DisplayTypes[value].value != failure.display_type:
                request.update_configuration(
                        f'failure_update({repr(selector)}, display_type={value.title()})')
                feedback = f"Le type d'affichage de «{selector}» est maintenant «{html.escape(value)}»\n"
        except KeyError:
            feedback += "Car invalide."
    elif incident.failure_id == 'failure-ask_confirm':
        if value != failure.ask_confirm:
            request.update_configuration(
                    f'failure_update({repr(selector)}, ask_confirm={repr(value)})')
            if value:
                feedback = f"On demande confirmation avant d'envoyer la panne «{selector}»\n"
            else:
                feedback = f"On ne demande pas confirmation à l'utilisateur avant d'envoyer la panne «{selector}»\n"
    elif incident.failure_id == 'failure-add':
        error_message = qrbug.Failure[selector].can_add_child(value)
        if error_message:
            feedback = f"<b>ERREUR :</b> {error_message}"
        else:
            if value not in qrbug.Failure.instances.keys():  # If the user doesn't exist, we create it !
                request.update_configuration(f'failure_update({repr(value)})')
            request.update_configuration(f'failure_add({repr(selector)}, {repr(value)})')
            feedback = f"Ajouté l'enfant «{html.escape(value)}» à «{selector}»\n"
    elif incident.failure_id == 'failure-remove':
        error_message = qrbug.Failure[value].can_remove_child(selector)
        if error_message:
            feedback = f"<b>ERREUR :</b> {error_message}"
        else:
            request.update_configuration(f'failure_remove({repr(value)}, {repr(selector)})')
            feedback = f"Retiré l'enfant «{selector}» à «{html.escape(value)}»\n"
    else:
        feedback = "Unexpected edit failure for Failure\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
