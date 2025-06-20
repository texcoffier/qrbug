"""
Display statistiques about QRBug
"""
import qrbug

async def run(_incidents, request):
    incidents = [
        j
        for i in qrbug.Incident.instances.values()
        for j in i.values()
        ]
    active = len([i for i in incidents if i.active])
    active_report = sum([len(i.active) for i in incidents])
    fixed_report = sum([len(i.finished) for i in incidents])
    feedback_pending = sum([len(i.pending_feedback.get((i.thing_id, i.failure_id), ()))
                            for i in incidents])
    def link(txt, add_len=True, add_link=True):
        if add_len:
            more = f'{len(getattr(qrbug, txt).instances)}</tr>'
        else:
            more = ''
        if add_link:
            txt = f'<a href="?what=thing&thing-id=admin&secret={request.secret.secret}&failure-id=list-{txt}">{txt}</a>'
        return f'<tr><td>{txt}<td>{more}'

    await request.write(
        f'''
        <table border>
        {link('Action')}
        {link('Concerned')}
        {link('Dispatcher')}
        {link('Failure')}
        {link('Selector')}
        {link('Thing')}
        {link('User')}
        {link('Secret', add_link=False)}
        {link('Incident', add_len=False)}
        {sum(len(i) for i in qrbug.Incident.instances.values())} types de panne différents<br>
        {active} pannes différents en cours<br>
        {active_report} ticket actif<br>
        {fixed_report} ticket corrigés<br>
        {feedback_pending} tickets sans retour pour dire que c'est réparé.
        </tr>
        </table>
        ''')

