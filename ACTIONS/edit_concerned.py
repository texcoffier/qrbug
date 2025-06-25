"""
In this case, the thing is a selector ID and the value an user.
"""
import html
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    user = html.escape(request.report.comment)
    if incident.failure_id == 'concerned-add':
        qrbug.append_line_to_journal(
                f'concerned_add({repr(selector)}, {repr(user)})\n', qrbug.Journals.DB)
        feedback = f"L'utilisateur/groupe «{html.escape(user)}» est maintenant concerné par le sélecteur «{html.escape(selector)}»\n"
    elif incident.failure_id == 'concerned-del':
        if user in incident.concerned.users:
            qrbug.append_line_to_journal(
                    f'concerned_del({repr(selector)}, {repr(user)})\n', qrbug.Journals.DB)
            feedback = f"L'utilisateur/groupe «{html.escape(user)}» n'est plus concerné par le sélecteur «{html.escape(selector)}»\n"
        else:
            feedback = f"L'utilisateur/groupe «{html.escape(user)}» <b>n'était pas</b> concerné par le sélecteur «{html.escape(selector)}»\n"
    else:
        feedback = "Unexpected edit failure for Concerned\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
