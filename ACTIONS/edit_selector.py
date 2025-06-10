"""
In this case, the thing is a selector ID to edit
"""
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = incident.active[-1].comment # Valid because no 'await' before
    if incident.failure_id == 'xxx':
        qrbug.append_line_to_journal(
                f'XXX({repr(selector)}, {repr(value)})\n', qrbug.Journals.DB)
        feedback = f"«{selector}»\n"
    else:
        feedback = "Unexpected edit failure for Selector\n"
    await request.response.write(b'<!DOCTYPE html>\n' + feedback.encode('utf-8'))
