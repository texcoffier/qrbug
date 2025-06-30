"""
In this case, the thing is a dispatcher ID to edit
"""
import html

import qrbug

TAG_NAME = 'pre'
FULL_TAG = f'<{TAG_NAME} style="display: inline;">'

async def run(incidents, request):
    incident = incidents[0]
    dispatcher_id = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'dispatcher-action_id':
        qrbug.append_line_to_journal(
                f'dispatcher_update({repr(dispatcher_id)}, action_id={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le nouvel {FULL_TAG}action_id</{TAG_NAME}> du dispatcher {FULL_TAG}{dispatcher_id}</{TAG_NAME}> est {FULL_TAG}{html.escape(value)}{FULL_TAG}.\n"
    elif incident.failure_id == 'dispatcher-selector_id':
        qrbug.append_line_to_journal(
                f'dispatcher_update({repr(dispatcher_id)}, selector_id={repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Le nouveeau {FULL_TAG}selector_id</{TAG_NAME}> du dispatcher {FULL_TAG}{dispatcher_id}</{TAG_NAME}> est {FULL_TAG}{html.escape(value)}</{TAG_NAME}>.\n"
    else:
        feedback = "Unexpected edit failure for Dispatcher\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
