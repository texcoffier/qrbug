"""
Display data on browser
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
    feedback_pending = sum([len(i.pending_feedback) for i in incidents])
    await request.write(
        f'''
        <table border>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Actions">Actions</a>
        <td>{len(qrbug.Action.instances)}</tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Concerned">Concerned</a>
        <td>{len(qrbug.Concerned.instances)}</tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Dispatcher">Dispatcher</a>
        <td>{len(qrbug.Dispatcher.instances)}</tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Failure">Failure</a>
        <td>{len(qrbug.Failure.instances)}</tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Incident">Incident</a>
        <td>
        {sum(len(i) for i in qrbug.Incident.instances.values())} types de panne différents<br>
        {active} pannes différents en cours<br>
        {active_report} ticket actif<br>
        {fixed_report} ticket corrigés<br>
        {feedback_pending} tickets sans retour pour dire que c'est réparé.
        </tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Selector">Selector</a>
        <td>{len(qrbug.Selector.instances)}</tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-Thing">Thing</a>
        <td>{len(qrbug.Thing.instances)}</tr>
        <tr><td>
        <a href="?what=thing&thing-id=admin&failure-id=list-User">User</a>
        <td>{len(qrbug.User.instances)}</tr>
        </table>
        ''')

