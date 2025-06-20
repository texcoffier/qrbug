"""
In this case, the thing is a dispatcher ID to edit
"""
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    dispatcher_id = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'dispatcher-action_id':
        qrbug.append_line_to_journal(
                f'dispatcher_update({repr(dispatcher_id)}, action_id={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le nouvel <i>action_id</i> du dispatcher {dispatcher_id} est {value}.\n"
    elif incident.failure_id == 'dispatcher-selector_id':
        qrbug.append_line_to_journal(
                f'dispatcher_update({repr(dispatcher_id)}, selector_id={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le nouveeau <i>selector_id</i> du dispatcher {dispatcher_id} est {value}.\n"
    else:
        feedback = "Unexpected edit failure for Dispatcher\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
