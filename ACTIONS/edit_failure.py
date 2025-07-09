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
            qrbug.append_line_to_journal(
                    f'failure_update({repr(selector)}, value={repr(value)})\n', qrbug.Journals.DB)
            feedback = f"Le titre de la panne «{selector}» est maintenant «{html.escape(value)}»\n"
    elif incident.failure_id == 'failure-display_type':
        try:
            if qrbug.DisplayTypes[value].value != failure.display_type:
                qrbug.append_line_to_journal(
                        f'failure_update({repr(selector)}, display_type={value.title()})\n', qrbug.Journals.DB)
                feedback = f"Le type d'affichage de «{selector}» est maintenant «{html.escape(value)}»\n"
        except KeyError:
            feedback += "Car invalide."
    elif incident.failure_id == 'failure-ask_confirm':
        if value != failure.ask_confirm:
            qrbug.append_line_to_journal(
                    f'failure_update({repr(selector)}, ask_confirm={repr(value)})\n', qrbug.Journals.DB)
            if value:
                feedback = f"On demande confirmation avant d'envoyer la panne «{selector}»\n"
            else:
                feedback = f"On ne demande pas confirmation à l'utilisateur avant d'envoyer la panne «{selector}»\n"
    else:
        feedback = "Unexpected edit failure for Failure\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
