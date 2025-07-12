"""
In this case, the thing is a selector ID to edit
"""
import html
import ast
import qrbug

async def run(incidents, request):
    incident = incidents[0]
    selector = incident.thing_id
    value = request.report.comment
    if incident.failure_id == 'selector-expression':
        try:
            ast.literal_eval(value)
            request.update_configuration(f'selector({repr(selector)}, {repr(value)})')
            feedback = f"Nouvelle valeur : <b><pre>{html.escape(value)}</pre></b>\n"
        except ValueError:
            feedback = f"Valeur invalide : <b><pre>{html.escape(value)}</pre></b>\n"
    elif incident.failure_id == 'selector-concerned-add':
        feedback = None
        if value not in qrbug.User.instances:
            feedback = await qrbug.User.try_create_user(request, value)
        if not feedback:
            request.update_configuration(
                    f'selector_concerned_add({repr(selector)}, {repr(value)})')
            feedback = f"L'utilisateur/groupe «{html.escape(value)}» est maintenant concerné par le sélecteur «{html.escape(selector)}»\n"
    elif incident.failure_id == 'selector-concerned-del':
        if value in incident.selector.concerned:
            request.update_configuration(
                    f'selector_concerned_del({repr(selector)}, {repr(value)})')
            feedback = f"L'utilisateur/groupe «{html.escape(value)}» n'est plus concerné par le sélecteur «{html.escape(selector)}»\n"
        else:
            feedback = f"L'utilisateur/groupe «{html.escape(value)}» <b>n'était pas</b> concerné par le sélecteur «{html.escape(selector)}»\n"
    else:
        feedback = "Unexpected edit failure for Selector\n"
    await request.write('<!DOCTYPE html>\n' + feedback)
