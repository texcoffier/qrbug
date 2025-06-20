"""
In this case, the thing is a dispatcher ID to edit
"""
import qrbug

BEACON_NAME = 'pre'
FULL_BEACON = f'<{BEACON_NAME} style="display: inline;">'

async def run(incidents, request):
    incident = incidents[0]
    dispatcher_id = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'dispatcher-action_id':
        qrbug.append_line_to_journal(
                f'dispatcher_update({repr(dispatcher_id)}, action_id={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le nouvel {FULL_BEACON}action_id</{BEACON_NAME}> du dispatcher {FULL_BEACON}{dispatcher_id}</{BEACON_NAME}> est {FULL_BEACON}{value}{FULL_BEACON}.\n"
    elif incident.failure_id == 'dispatcher-selector_id':
        qrbug.append_line_to_journal(
                f'dispatcher_update({repr(dispatcher_id)}, selector_id={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le nouveeau {FULL_BEACON}selector_id</{BEACON_NAME}> du dispatcher {FULL_BEACON}{dispatcher_id}</{BEACON_NAME}> est {FULL_BEACON}{value}</{BEACON_NAME}>.\n"
    else:
        feedback = "Unexpected edit failure for Dispatcher\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
