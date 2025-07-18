import time
import html
import sys
import random
from pathlib import Path
from typing import Optional

import asyncio
from aiohttp import web

import qrbug.init
import qrbug


ENABLE_AUTHENTICATION = True
ENABLE_PROFILE = False

WHAT = {
    'thing': qrbug.Thing,
    'dispatcher': qrbug.Dispatcher,
    'failure': qrbug.Failure,
    'selector': qrbug.Selector,
    'user': qrbug.User,
    'action': qrbug.Action,
}

async def hourly_task():
    while True:
        now = time.time()
        next_hour = time.strftime('%Y%m%d%H', time.localtime(now + 3600))
        wait_seconds = time.mktime(time.strptime(next_hour, '%Y%m%d%H')) - now
        # wait_seconds = 1
        await asyncio.sleep(wait_seconds)
        incident = qrbug.Incident.open('GUI', f'${next_hour[-2:]}:00', '', '@system', '')
        request = qrbug.FakeRequest(incident, create_secret=False)
        for dispatcher in qrbug.Dispatcher.get_sorted_instances():
            await dispatcher.run(incident, request, [])
        qrbug.Secret.cleanup()

async def show_failures_tree_route(request: qrbug.Request) -> web.Response:
    """
    Returns the webpage listing the failure hierarchy for the given thing.
    """
    print(request.path_qs)

    what: Optional[str] = request.match_info.get("what", None)
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    secret: Optional[str] = request.query.get('secret', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing = WHAT[what][thing_id]
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")

    request.secret = qrbug.update_secret(secret)
    request.write = lambda text: request.response.write(text.encode('utf-8'))
    return web.Response(status=200, text=requested_thing.get_failures(request.secret), content_type='text/html')


async def register_incident(request: qrbug.Request) -> web.StreamResponse:
    """
    Registers an incident into the logs, then shows the user that the incident has been registered.
    """
    print(request.path_qs)
    what: Optional[str] = request.query.get("what", 'thing')
    thing_id: Optional[str] = request.query.get("thing-id", None)
    failure_id: Optional[str] = request.query.get("failure-id", None)
    is_repaired: Optional[str] = request.query.get("is-repaired", '0')
    secret: Optional[str] = request.query.get("secret", None)
    additional_info: Optional[str] = request.query.get("additional-info", '')

    secret = qrbug.check_secret(secret)
    if ENABLE_AUTHENTICATION:
        if not secret:
            return web.Response(status=404,
                text="Votre session a expiré, rechargez la page listant les pannes.")
    else:
        if not secret:
            secret = qrbug.update_secret('unittest_secret')
            secret.login = 'ROOT'

    if thing_id is None:
        return web.Response(status=404, text="thing_id is undefined")
    if failure_id is None:
        return web.Response(status=404, text="failure_id is undefined")

    # Checks for existence
    failure = qrbug.Failure[failure_id]
    if failure is None:
        return web.Response(status=404, text="Failure does not exist")

    if not WHAT[what][thing_id]:
        return web.Response(status=404, text=f"{what}[{thing_id}] does not exist")

    user_ip = request.remote
    # Cas authentication
    user_login = secret.login
    if not user_login:
        if ENABLE_AUTHENTICATION:
            incident = qrbug.Incident(thing_id, failure_id)
            incident.active.append(qrbug.Report(user_ip, 0, additional_info, user_login))
            if qrbug.Selector['?require-login'].is_ok(incident, incident.active[0]):
                user_login = await qrbug.get_login(secret.secret, request.query, request.path_qs)
                if not user_login:
                    query_variables = {
                        'what': what,
                        'thing_id': thing_id,
                        'failure_id': failure_id,
                        'is_repaired': is_repaired,
                        'additional_info': additional_info,
                        'secret': secret.secret
                    }
                    # REDIRECT CAS
                    params = '&'.join(f'{name.replace("_", "-")}={value}'
                                    for name, value in query_variables.items())
                    qrbug.redirect(f'?{params}')
                    raise Exception("Redirection failed")
        else:
            user_login = 'ROOT' # For tests
            secret.login = user_login
    is_repaired_bool: bool = is_repaired == '1'

    if is_repaired_bool:
        current_incident = qrbug.Incident.close(thing_id, failure_id, user_ip, user_login)
        return web.Response(status=200, text='<style>BODY {margin:0px}</style>👍', content_type='text/html')
    else:
        current_incident = qrbug.Incident.open(thing_id, failure_id, user_ip, user_login, additional_info)
        request.report = current_incident.active[-1]
        request.incident = current_incident

    # Starts preparing the response
    request.secret = secret
    request.response = web.StreamResponse(
        status=200,
        headers={'Content-Type': 'text/html; charset=utf-8'},
    )
    request.write = lambda text: request.response.write(text.encode('utf-8'))
    request.write_newline = lambda *text: request.write('\n'.join(text))
    request.update_configuration = lambda line: qrbug.append_line_to_journal(
        f'{line} # {request.report.login} {time.strftime("%Y-%m-%d %H:%M:%S")} {request.report.ip}\n',
        qrbug.Journals.DB)
    await request.response.prepare(request)

    # Dispatchers
    returned_html: dict[str, Optional[qrbug.action_helpers.ActionReturnValue]] = {}
    trace = ['<!-- ',
        html.escape(current_incident.thing_id), ' ',
        html.escape(current_incident.failure_id), ' ',
        html.escape(request.report.comment), ' ',
        html.escape(request.report.login)]
    if not is_repaired_bool:
        for dispatcher in qrbug.Dispatcher.get_sorted_instances():
            trace.append(f' -->\n<!-- {dispatcher.id}#{dispatcher.selector_id} {current_incident.thing_id}/{current_incident.failure_id}: {request.report.login}')
            returned_html[dispatcher.id] = await dispatcher.run(current_incident, request, trace)
    trace.append('-->')
    await request.write(''.join(trace))

    if any(value is not None for value in returned_html.values()):
        await request.write('Informations additionnelles :')

    # Makes the HTML response from the dispatchers
    INDENT_SIZE_PIXELS = 20
    for dispatcher_id, dispatcher_return_value in returned_html.items():
        if dispatcher_return_value is not None:
            await request.write(
                f'<p>DISPATCHER [{dispatcher_id}]<br/>\n'
            )
            await request.write((
                f'<div style="padding-left: {INDENT_SIZE_PIXELS}px;">\n'
                f'    INCIDENT [{current_incident.thing_id}, {current_incident.failure_id}]\n'
            ))

            response_values = [  # (title, value)
                ('ERROR', dispatcher_return_value.error_msg),
                ('INFO', dispatcher_return_value.info_msg),
            ]
            for title, response_value in response_values:
                if response_value:
                    await request.write((
                        f'    <div style="padding-left: {INDENT_SIZE_PIXELS * 2}px;">\n'
                        f'        <h3>{title}</h3>\n'
                        f'        <div style="padding-left: {INDENT_SIZE_PIXELS * 3}px;">{response_value}</div>\n'
                        f'    </div>\n'
                    ))
            await request.write('</div>\n')
            await request.write('</p>\n')

    # return_string = (f"thing_id={thing_id}\n"
    #                  f"failure_id={failure_id}\n"
    #                  f"is_repaired={is_repaired_bool}\n"
    #                  f"additional_info={additional_info}\n\n"
    #                  f"valid_request={valid_request}\n\n"
    #                  f"Registered new incident.")
    # return web.Response(status=200, text=return_string)
    await request.response.write_eof()
    return request.response


async def get_favicon(_request: web.Request) -> web.Response:
    return web.Response(
        status=200,
        body=qrbug.FAVICON_PATH.read_bytes(),
        content_type='image/ico'
    )


def parse_command_line_args(argv) -> tuple[str, int]:
    """
    Parses the command line args and returns them.
    :param argv: The command line args.
    :return: The host and port that should be used by the server.
    """
    args = argv.copy()  # In order not to modify the original args

    if '--test' in args:  # The --test flag allows for serialized testing with test.sh
        global ENABLE_AUTHENTICATION
        ENABLE_AUTHENTICATION = False

        qrbug.DB_FILE_PATH = Path('TESTS/xxx-db.py')
        if '--testload' in args:
            qrbug.DB_FILE_PATH.write_bytes(Path('TESTS/xxx-testload.conf').read_bytes())
            args.remove('--testload')
        else:
            qrbug.DB_FILE_PATH.write_bytes(Path('TESTS/test_server_db.conf').read_bytes())
        qrbug.INCIDENTS_FILE_PATH = Path('TESTS/xxx-incidents.py')
        args.remove('--test')

    if '--profile' in sys.argv:
        global ENABLE_PROFILE
        ENABLE_PROFILE=True
        args.remove('--profile')

    host = qrbug.HOST
    port = qrbug.PORT
    if len(args) >= 2:
        host = args[1]
    if len(args) >= 3:
        port = int(args[2])
    return host, port


def init_server(argv = None) -> tuple[web.Application, str, int]:
    """
    Function that will be run on server startup.
    Loads the config and incidents journals, starts a new server, and creates the routes.
    """
    if argv is None:
        argv = []

    host, port = parse_command_line_args(argv)

    if ENABLE_PROFILE:
        import profile
        print("PROFILING LOADING CONFIG AND INCIDENTS")
        profile.run("qrbug.load_config(); qrbug.load_incidents()", sort=1)
    else:
        # Loads the config
        start = time.time()
        qrbug.load_config()
        qrbug.load_incidents()
        print(f'Load journals : {time.time() - start:.2f} seconds')

    # Creates the server
    app = web.Application()
    app.add_routes([
        web.get('/{what:thing|dispatcher|failure|selector|user|action}={thing_id:[^{}?]+}', show_failures_tree_route),
        web.get('/', register_incident),
        web.get('/favicon.ico', get_favicon)
    ])
    if ENABLE_AUTHENTICATION:
        async def on_startup(_app):
            asyncio.create_task(hourly_task())
        app.on_startup.append(on_startup)
    return app, host, port

def get_server(argv: list = None) -> web.Application:
    """
    Function called by server starting scripts to launch the server

    ⚠️ RETURNS A web.Application ONLY ⚠️
    This is required by the server starting framework.
    """
    if argv is None:
        argv = []
    return init_server(argv)[0]

def main():
    random.seed()
    server, host, port = init_server(sys.argv)
    web.run_app(server, host=host, port=port)

if __name__ == "__main__":

    if '-h' in sys.argv or '--help' in sys.argv:
        print("Usage: python -m qrbug.server [--test] [HOST] [PORT]")
        print("\n--test : Use the test databases.")
    main()
