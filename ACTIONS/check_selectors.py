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
        infos = collections.defaultdict(set)
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
                        except: # pylint: disable=bare-except
                            # import traceback
                            # traceback.print_exc()
                            active = '?'
                        infos[active].add((report.login, incident.thing_id, incident.active, incident.failure_id))

        def all_here(logins, thing_ids, actives, failure_ids):
            for login in logins:
                for thing_id in thing_ids:
                    for active in actives:
                        for failure_id in failure_ids:
                            if (login, thing_id, active, failure_id) not in items:
                                return False
            for login in logins:
                for thing_id in thing_ids:
                    for active in actives:
                        for failure_id in failure_ids:
                            items.discard((login, thing_id, active, failure_id))
            return True

        for is_ok, items in infos.items():
            if not is_ok:
                continue
            while items:
                login, thing_id, active, failure_id = items.pop()
                logins = [login]
                thing_ids = [thing_id]
                actives = [active]
                failure_ids = [failure_id]

                for login in LOGINS:
                    if all_here([login], thing_ids, actives, failure_ids):
                        logins.append(login)

                for thing_id in THINGS:
                    if all_here(logins, [thing_id], actives, failure_ids):
                        thing_ids.append(thing_id)

                for active in ACTIVES:
                    if all_here(logins, thing_ids, [active], failure_ids):
                        actives.append(active)

                for failure_id in FAILURES:
                    if all_here(logins, thing_ids, actives, [failure_id]):
                        failure_ids.append(failure_id)

                failures = [is_ok if failure in failure_ids else ''
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
        previous_line = lines[0]
        merged = []
        for line in lines[1:]:
            if line[:3] == previous_line[:3]:
                merge = []
                for a, b in zip(line[3], previous_line[3]):
                    if a and b:
                        break
                    if a:
                        merge.append(a)
                    else:
                        merge.append(b)
                else:
                    previous_line[3] = merge
                    continue # Do not add line
            merged.append(previous_line)
            previous_line = line
        merged.append(previous_line)
        lines = merged
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
