"""
Display if selectors are True or False
"""

# pylint: disable=consider-using-f-string

import asyncio
import html
import collections
import qrbug

def nice(ids):
    ids = '+'.join(sorted(str(i).split(".", 1)[0]
                          for i in ids
                         )
                  )
    if ids == 'admin-thing+admin-user+nobody+root':
        return '*'
    if ids == 'admin-thing+admin-user+nobody':
        return '*-root'
    if ids == 'admin+b751pc0404+root':
        return '*'
    if ids == 'admin+b751pc0404':
        return '*-root'
    if ids == '()+(42,)':
        return '*'
    if ids == '()':
        return 'non'
    if ids == '(42,)':
        return 'oui'
    return html.escape(ids)

IS_OK = {'*': 'ok', '!': 'other', '#': 'rejected', '': ''}
def create(line):
    failures = []
    for j, is_ok in enumerate(line[3]):
        failures.append(f'<td class="c{j} {IS_OK.get(is_ok, "bug")}">')
    failures = ''.join(failures)
    return f'<td>{nice(line[0])}<td>{nice(line[1])}<td>{nice(line[2])}{failures}'

async def run(_incidents, request):
    incident = qrbug.Incident('', '')
    report = qrbug.incident.Report('', 0)
    LOGINS = ('nobody', 'root', 'admin-user', 'admin-thing')
    THINGS = ('admin', 'b751pc0404.univ-lyon1.fr', 'root')
    ACTIVES = ((), (42,))
    FAILURES = sorted(qrbug.Failure.instances, key=lambda x: qrbug.Failure.instances[x].path())

    await request.write(
        """
    <style>
    BODY { font-family: sans-serif }
    TABLE { border-spacing: 0px }
    .vert DIV {
        transform: rotate(-45deg); margin-top: 40px; width: 8px;
        font-weight: normal; white-space: nowrap; font-size: 50% }
    TR:first-child { position: sticky; top: 0px; background: #FFF }
    TR:nth-child(2) { position: sticky; top: 70px; background: #FFF }
    TR TH { height: 4.5em }
    TR TD { border: 1px solid #FFF; font-size: 80%; padding-top: 0px; padding-bottom: 0px }
    TR TD.selector { font-size: 100% }
    TR.gray { background: #EEE }
    TR:hover TD { border-top-color: #000; border-bottom-color: #000 }
    .ok { background: #8F8 }
    .other { background: #DFD }
    .rejected { background: #FB8 }
    .bug { background: #FAA }
    .bigbug { background: #000 }
    </style>
    <style id="style">
    </style>
    <h1>Conditions activant un sélecteur</h1>
    <ul>
    <li> Rouge: bug.
    <li> Vert: Actif (True).
    <li> Vert clair: Actif (!=True).
    <li> Orange: sélecteur actif, mais la panne ne l'accepte pas.
    <li> Blanc: inactif.
    </ul>
    <p>
    Les lignes blanches ne sont pas affichées.
    <p>
    * : représente tous les cas. Sinon le cas qui a été testé.""")
    selectors = collections.defaultdict(list)
    for selector_id, selector in sorted(qrbug.Selector.instances.items()):
        infos = {}
        for report.login in LOGINS:
            for incident.thing_id in THINGS:
                for incident.active in ACTIVES:
                    for incident.failure_id in FAILURES:
                        try:
                            active = selector.is_ok(incident, incident, report)
                            if active:
                                if isinstance(active, str):
                                    active = active[0]
                                else:
                                    if active is True:
                                        active = '*'
                                    else:
                                        active = '!'
                                    if not qrbug.Selector[incident.failure.allowed
                                            ].is_ok(incident, report=report):
                                        active = '#'
                            else:
                                active = ''
                        except: # pylint: disable=bare-except
                            # import traceback
                            # traceback.print_exc()
                            active = '?'
                        infos[report.login, incident.thing_id, incident.active, incident.failure_id] = active

        def all_here(logins, thing_ids, actives, failure_ids, is_ok):
            for login in logins:
                for thing_id in thing_ids:
                    for active in actives:
                        for failure_id in failure_ids:
                            if keep[login, thing_id, active, failure_id] != is_ok:
                                return False
            for login in logins:
                for thing_id in thing_ids:
                    for active in actives:
                        for failure_id in failure_ids:
                            infos.pop((login, thing_id, active, failure_id), None)
            return True

        keep = dict(infos)
        while infos:
            login, thing_id, active, failure_id = next(iter(infos))
            is_ok = infos.pop((login, thing_id, active, failure_id))
            if not is_ok:
                continue
            logins = [login]
            thing_ids = [thing_id]
            actives = [active]
            failure_ids = [failure_id]

            for login in LOGINS:
                if login not in logins:
                    if all_here([login], thing_ids, actives, failure_ids, is_ok):
                        logins.append(login)

            for thing_id in THINGS:
                if thing_id not in thing_ids:
                    if all_here(logins, [thing_id], actives, failure_ids, is_ok):
                        thing_ids.append(thing_id)

            for active in ACTIVES:
                if active not in actives:
                    if all_here(logins, thing_ids, [active], failure_ids, is_ok):
                        actives.append(active)

            for failure_id in FAILURES:
                if failure_id not in failure_ids:
                    if all_here(logins, thing_ids, actives, [failure_id],
                                keep[logins[0], thing_ids[0], actives[0], failure_id]):
                        failure_ids.append(failure_id)

            failures = [keep[logins[0],thing_ids[0], actives[0], failure] if failure in failure_ids else ''
                        for failure in FAILURES]
            selectors[selector_id].append([sorted(logins), sorted(thing_ids), sorted(actives), failures])

        await asyncio.sleep(0)

    await request.write("""
    <table id="table">
    <tr><th rowspan="2">Selector<th rowspan="2">Login<th rowspan="2">Thing<th rowspan="2">Active<th colspan="%d">Failures
    <tr>
    """ % (len(FAILURES)+4))
    await request.write(''.join(
        f'<th class="c{i} vert"><div>{html.escape(selector_id)}</div>'
        for i, selector_id in enumerate(FAILURES)))
    await request.write('</tr>')
    for i, (selector_id, lines) in enumerate(sorted(selectors.items(), key=lambda x: x[1][0][3], reverse=True)):
        if i % 2:
            tr = '<tr class="gray">'
        else:
            tr = '<tr>'
        lines.sort()
        lasts = ''.join(f'{tr}{create(i)}' for i in lines[1:])
        await request.write(
            f'{tr}<td class="selector" rowspan="{len(lines)}">{selector_id}{create(lines[0])}{lasts}'
        )

    await request.write("""</table>
    <script>
    var style = document.getElementById('style');
    function enter(event) {
        if (event.target.tagName == 'TD' || event.target.tagName == 'TH' ) {
            var cls = event.target.className.split(' ')[0];
            style.textContent = 'TD.' + cls + '{border-left-color: #000; border-right-color: #000}'
                              + 'TH.' + cls + ' DIV{font-weight: bold; font-size: 130%}'
            }
    }
    window.addEventListener('mousemove', enter);
    </script>
    """)
