"""
In this case, the thing is a user ID to edit
"""
import html

import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = html.escape(request.report.comment)
    if incident.failure_id == 'xxx':
        qrbug.append_line_to_journal(
                f'XXX({repr(selector)}, {repr(value)})\n', qrbug.Journals.DB)
        feedback = f"«{selector}»\n"
    else:
        feedback = "Unexpected edit failure for User\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
