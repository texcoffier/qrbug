"""
In this case, the thing is an action ID to edit
"""
from pathlib import Path
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = incident.active[-1].comment # Valid because no 'await' before
    if incident.failure_id == 'action-python_script':
        if Path('ACTIONS', value).exists():
            if value == qrbug.Action[selector].python_script:
                feedback = f"Le script Python de l'action «{selector}» est inchangé.\n"
            else:
                qrbug.append_line_to_journal(
                        f'action({repr(selector)}, {repr(value)})\n', qrbug.Journals.DB)
                feedback = f"L'action «{selector}» lance maintenant le script «{value}»\n"
        else:
            feedback = f"Le script Python «{value}» n'existe pas.\n"
    else:
        feedback = "Unexpected edit failure for Action\n"
    await request.response.write(feedback.encode('utf-8'))
