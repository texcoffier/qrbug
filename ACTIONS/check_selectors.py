"""
Display if selectors are True or False
"""

# pylint: disable=consider-using-f-string

import asyncio
import html
import collections
import traceback
import qrbug

IS_OK = {'*': 'ok', '!': 'other', '': ''}

async def run(_incidents, request):
    incident = qrbug.Incident('', '')
    report = qrbug.incident.Report('', 0)
    LOGINS = sorted(qrbug.Failure['$check_selector_logins'].value.split(' '))
    THINGS = sorted(qrbug.Failure['$check_selector_things'].value.split(' '))
    ACTIVES = ((), (42,))
    FAILURES = sorted(qrbug.Failure.instances, key=lambda x: qrbug.Failure.instances[x].path())

    def create(line):
        values = (
            *(('login yes', '') if login in line[0] else ('login no', '') for login in LOGINS),
            *(('thing yes', '') if thing in line[1] else ('thing no', '') for thing in THINGS),
            *(('state yes', '') if state in line[2] else ('state no', '') for state in ((42,), ())),
            *((IS_OK.get(is_ok, 'bug'), f'<PRE>{html.escape(is_ok)}</PRE>' if is_ok not in IS_OK else '') for is_ok in line[3])
        )
        return ''.join(f'<td class="c{i} {classe}">{value}' for i, (classe, value) in enumerate(values))

    await request.write(
        """
    <style>
    BODY { font-family: sans-serif }
    TABLE { border-spacing: 0px }
    .vert DIV {
        transform: rotate(-45deg); margin-top: 40px; width: 14px;
        font-weight: normal; white-space: nowrap; font-size: 70% }
    TR:first-child { position: sticky; top: 0px; background: #FFF; z-index: 100 }
    TR:nth-child(2) { position: sticky; top: 70px; background: #FFF; z-index: 100 }
    TR TD.selector { position: sticky; left: 0px; background: inherit; white-space: nowrap }
    TR TH { height: 4.5em }
    TR TD { border: 1px solid #FFF; padding-top: 0px; padding-bottom: 0px; height: 1em; }
    TR.gray, TR TD.selector { background: #EEE }
    TR:hover TD { border-top-color: #000; border-bottom-color: #000 }
    TD PRE { display: none ; position: absolute; background: #FDD }
    TD:hover PRE { display: block ; }
    .ok { background: #8F8 }
    .other { background: #DFD }
    .rejected { background: #FB8 }
    .bug { background: #FAA }
    .bigbug { background: #000 }
    .login { background: #88F }
    .thing { background: #BB0 }
    .state { background: #0BB }
    .no { background: #FFF}
    PLUS, MINUS { display: inline; margin-left: 0.2em }
    PLUS { background-color: #8F8 }
    MINUS { background-color: #FAA }
    </style>
    <style id="style">
    </style>
    <h1>Conditions activant un sélecteur</h1>
    <ul>
    <li> Rouge: bug (mettre le curseur dessus pour voir l'exception).
    <li> Vert: Actif (True).
    <li> Vert clair: Actif (!=True).
    <li> Orange: sélecteur actif, mais la panne ne l'accepte pas.
    <li> Blanc: inactif.
    </ul>
    <p>
    Les lignes blanches ne sont pas affichées.
    <p>
    La liste des logins et des choses à tester sont modifiable dans
    les pannes '$check_selector_logins' et '$check_selector_things'
    """)
    selectors = collections.defaultdict(list)
    for selector_id, selector in sorted(qrbug.Selector.instances.items()):
        infos = {}
        errors = {}
        for report.login in LOGINS:
            for incident.thing_id in THINGS:
                for incident.active in ACTIVES:
                    for incident.failure_id in FAILURES:
                        try:
                            active = selector.is_ok(incident, report, incident)
                            if active:
                                if isinstance(active, str):
                                    active = active[0]
                                else:
                                    if active is True:
                                        active = '*'
                                    else:
                                        active = '!'
                            else:
                                active = ''
                        except: # pylint: disable=bare-except
                            # import traceback
                            # traceback.print_exc()
                            active = traceback.format_exc()
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

        def mergeable_logins(login1, login2, thing_ids, actives, failure_ids):
            for thing_id in thing_ids:
                for active in actives:
                    for failure_id in failure_ids:
                        if keep[login1, thing_id, active, failure_id] != keep[login2, thing_id, active, failure_id]:
                            return False
            for thing_id in thing_ids:
                for active in actives:
                    for failure_id in failure_ids:
                        infos.pop((login2, thing_id, active, failure_id), None)
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

            for login in LOGINS:
                if login not in logins:
                    if mergeable_logins(logins[0], login, thing_ids, actives, failure_ids):
                        logins.append(login)

            failures = [keep[logins[0],thing_ids[0], actives[0], failure] if failure in failure_ids else ''
                        for failure in FAILURES]
            selectors[selector_id].append([sorted(logins), sorted(thing_ids), sorted(actives), failures])

        await asyncio.sleep(0)

    await request.write("""
    <table id="table">
    <tr><th rowspan="2">Selector<th colspan="%d">Logins<th colspan="%d">Things<th colspan="%d">?<th colspan="%d">Failures
    <tr>
    """ % (
        len(LOGINS), len(THINGS), 2, len(FAILURES)+4
        ))

    values = (*LOGINS, *THINGS, 'Active', 'Fixed', *FAILURES)

    await request.write(''.join(
        f'<th class="c{i} vert"><div>{html.escape(value)}</div>'
        for i, value in enumerate(values)))

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
