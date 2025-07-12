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
        request.update_configuration(
                f'thing_update({repr(selector)}, comment={repr(value)})')
        feedback = f"Le commentaire est maintenant «{html.escape(value)}»\n"
    elif incident.failure_id == 'thing-del-failure':
        if value in incident.thing.failure_ids:
            request.update_configuration(
                f'thing_del_failure({repr(selector)}, {repr(value)})')
            feedback = f"La panne «{html.escape(value)}» a été enlevée.\n"
        else:
            feedback = "La panne n'était pas présente"
    elif incident.failure_id == 'thing-add-failure':
        if value in qrbug.Failure.instances:
            request.update_configuration(
                f'thing_add_failure({repr(selector)}, {repr(value)})')
            feedback = f"La panne «{html.escape(value)}» a été ajoutée.\n"
        else:
            feedback = "Cette panne n'existe pas"
    elif incident.failure_id == 'thing-add':
        error_message = qrbug.Thing[selector].can_add_child(value)
        if error_message:
            feedback = f"<b>ERREUR :</b> {error_message}"
        else:
            if value not in qrbug.Thing.instances.keys():  # If the user doesn't exist, we create it !
                request.update_configuration(f'thing_update({repr(value)})')
            request.update_configuration(f'thing_add({repr(selector)}, {repr(value)})')
            feedback = f"Ajouté l'enfant «{html.escape(value)}» à «{selector}»\n"
    elif incident.failure_id == 'thing-remove':
        error_message = qrbug.Thing[value].can_remove_child(selector)
        if error_message:
            feedback = f"<b>ERREUR :</b> {error_message}"
        else:
            request.update_configuration(f'thing_remove({repr(value)}, {repr(selector)})')
            feedback = f"Retiré l'enfant «{selector}» à «{html.escape(value)}»\n"
    else:
        feedback = "Unexpected edit failure for Thing\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
