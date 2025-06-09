"""
In this case, the thing is a selector ID and the value an user.
"""
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    user = incident.active[-1].comment # Valid because no 'await' before
    if incident.failure_id == 'concerned-add':
        qrbug.append_line_to_journal(
                f'concerned_add({repr(selector)}, {repr(user)})\n', qrbug.Journals.DB)
        feedback = f"L'utilisateur/groupe «{user}» est maintenant concerné par le sélecteur «{selector}»\n"
    elif incident.failure_id == 'concerned-del':
        qrbug.append_line_to_journal(
                f'concerned_del({repr(selector)}, {repr(user)})\n', qrbug.Journals.DB)
        feedback = f"L'utilisateur/groupe «{user}» n'est plus concerné par le sélecteur «{selector}»\n"
    else:
        feedback = "Unexpected edit failure for Concerned"
    await request.response.write(feedback.encode('utf-8'))
