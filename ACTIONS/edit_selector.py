"""
In this case, the thing is a selector ID to edit
"""
import html

import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'selector-expression':
        qrbug.append_line_to_journal(f'selector({repr(selector)}, {repr(value)})\n', qrbug.Journals.DB)
        feedback = f"Nouvelle valeur : <b><pre>{html.escape(value)}</pre></b>\n"
    else:
        feedback = "Unexpected edit failure for Selector\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
