"""
In this case, the thing is a dispatcher ID to edit
"""
import html
import pathlib
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    dispatcher_id = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'dispatcher-action_id':
        feedback = None
        if value not in qrbug.Action.instances:
            script = value + '.py'
            if pathlib.Path('ACTIONS', script).exists():
                request.update_configuration(f'action({repr(value)}, {repr(script)})')
            else:
                feedback = f"Le script Python «{script}» n'existe pas.\n"
        if not feedback:
            request.update_configuration(
                f'dispatcher_update({repr(dispatcher_id)}, action_id={repr(value)})')
            feedback = f"La nouvelle action du dispatcher «{dispatcher_id}» est «{html.escape(value)}».\n"
    elif incident.failure_id == 'dispatcher-selector_id':
        message = qrbug.Selector.create_if_needed(value)
        request.update_configuration(
            f'dispatcher_update({repr(dispatcher_id)}, selector_id={repr(value)})')
        feedback = f"Le nouveau selecteur du dispatcher «{dispatcher_id}» est «{html.escape(value)}».\n<br>{message}"
    elif incident.failure_id == 'dispatcher-incidents':
        message = qrbug.Selector.create_if_needed(value)
        request.update_configuration(
            f'dispatcher_update({repr(dispatcher_id)}, incidents={repr(value)})')
        feedback = f"Le nouveau selecteur d'incidents de «{dispatcher_id}» est «{html.escape(value)}».\n<br>{message}"
    elif incident.failure_id == 'dispatcher-new':
        if value in qrbug.Dispatcher.instances:
            feedback = "Cet automatisme existe déjà"
        else:
            request.update_configuration(f'dispatcher_update({repr(value)})')
            feedback = "<script>window.top.location.reload()</script>"
    else:
        feedback = "Unexpected edit failure for Dispatcher\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
