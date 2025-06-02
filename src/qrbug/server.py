import datetime
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiohttp import web

import qrbug.init
import qrbug


ENABLE_AUTHENTICATION = True


async def show_failures_tree_route(request: web.Request) -> web.Response:
    """
    Returns the webpage listing the failure hierarchy for the given thing.
    """
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing: Optional[qrbug.Thing] = qrbug.Thing[thing_id]
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")

    # Creates the CAS login
    if ENABLE_AUTHENTICATION:
        user_login = await qrbug.handle_login(request, f'thing={thing_id}')
        if user_login is None:
            return web.Response(status=403, text="Login ticket invalid")

    #return web.Response(status=200, text=f"Thing ID: {thing_id}\n\n{requested_thing.dump()}\n\nFailures list :\n{get_failures(thing_id)}")
    # TODO : Groupe autorisé à déclarer la panne
    if thing_id == 'debug':
        return web.Response(status=200, text=qrbug.Thing[thing_id].get_failures(as_html=False))
    return web.Response(status=200, text=qrbug.Thing[thing_id].get_failures(), content_type='text/html')


async def register_incident(request: web.Request) -> web.StreamResponse:
    """
    Registers an incident into the logs, then shows the user that the incident has been registered.
    """
    thing_id: Optional[str] = request.query.get("thing-id", None)
    failure_id: Optional[str] = request.query.get("failure-id", None)
    is_repaired: Optional[str] = request.query.get("is-repaired", None)
    additional_info: Optional[str] = request.query.get("additional-info", None)

    query_variables = {
        'thing_id': thing_id,
        'failure_id': failure_id,
        'is_repaired': is_repaired,
    }
    valid_request = all(query_variables.values())
    if valid_request is False:
        return web.Response(status=404, text=f"Missing query parameters : " + ", ".join(
            (query_param for query_param, query_param_value in query_variables.items() if query_param_value is None)
        ))

    # Checks for existence
    failure = qrbug.Failure[failure_id]
    if failure is None:
        return web.Response(status=404, text=f"Failure does not exist")
    if qrbug.Thing[thing_id] is None:
        return web.Response(status=404, text=f"Thing does not exist")

    # Cas authentication
    user_token = request.query.get("token", None)
    user_login = ''
    if ENABLE_AUTHENTICATION:
        if failure.restricted_to_group_id is not None:  # Only authenticate if failure requires it
            if user_token is not None:
                user_login = qrbug.get_login_from_token(user_token, request.remote)
            if not user_login:
                user_login = await qrbug.handle_login(request, f'thing={thing_id}')
                if user_login is None:
                    return web.Response(status=403, text="Login ticket invalid")

    is_repaired_bool: bool = is_repaired == '1'
    timestamp = int(time.time())
    current_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    function_name = "incident_del" if is_repaired_bool else "incident"  # TODO: Refactor
    user_ip = request.remote

    function_to_log = f"{function_name}({repr(thing_id)}, {repr(failure_id)}, {repr(user_ip)}, {timestamp}"
    if is_repaired_bool is False:
        if additional_info is not None:
            # incident_del() does not take additional_info as parameter,
            # therefore if the incident is repaired, we must ABSOLUTELY NOT get into this if block
            # if this incident is resolved
            function_to_log += f", {repr(additional_info)}"
    else:
        function_to_log += f", {repr(user_login)}"
    function_to_log += f")  # {current_date} {user_login}\n"

    current_incident = qrbug.append_line_to_journal(function_to_log)

    # if failure.auto_close_incident:  # TODO: Move after dispatch_del
    #     qrbug.append_line_to_journal(f'incident_del({repr(thing_id)}, {repr(failure_id)}, {repr(user_ip)}, {timestamp}, {repr(user_login)})  # {current_date} {user_login}\n')

    # TODO: Run on incident repaired
    # TODO: Envoyer un mail à la personne qui a signalé la panne

    # Starts preparing the response
    request.response = web.StreamResponse(
        status=200,
        headers={'Content-Type': 'text/html; charset=utf-8'},
    )
    await request.response.prepare(request)
    await request.response.write("<h1>Merci !</h1><h3>Votre signalement a été enregistré.</h3>".encode('utf-8'))

    # Dispatchers
    returned_html: dict[str, Optional[str]] = {}
    if not is_repaired_bool:
        for dispatcher in qrbug.Dispatcher.instances.values():
            if dispatcher.when == 'synchro':
                returned_html[dispatcher.id] = await dispatcher.run(current_incident, request)
            else:
                pass # TODO: Rajouter la fonction dispatch au journal d'incidents

    if any(value is not None for value in returned_html.values()):
        await request.response.write(b'Informations additionnelles :')

    # Makes the HTML response from the dispatchers
    for dispatcher_id, dispatcher_return_value in returned_html.items():
        if dispatcher_return_value is not None:
            await request.response.write(
                f'<p>DISPATCHER [{dispatcher_id}]<br/>'.encode('utf-8')
            )
            await request.response.write((
                f'<div style="padding-left: 20px;">INCIDENT [{current_incident.thing_id}, {current_incident.failure_id}]'
                f'    <div style="padding-left: 40px;">{dispatcher_return_value}</div>'
                f'</div>'
            ).encode('utf-8'))
            await request.response.write(b'</p>')

    # return_string = (f"thing_id={thing_id}\n"
    #                  f"failure_id={failure_id}\n"
    #                  f"is_repaired={is_repaired_bool}\n"
    #                  f"additional_info={additional_info}\n\n"
    #                  f"valid_request={valid_request}\n\n"
    #                  f"Registered new incident.")
    # return web.Response(status=200, text=return_string)
    await request.response.write_eof()
    return request.response


def parse_command_line_args(argv) -> tuple[str, int]:
    """
    Parses the command line args and returns them.
    :param argv: The command line args.
    :return: The host and port that should be used by the server.
    """
    args = argv.copy()  # In order not to modify the original args

    if '--test' in args:  # The --test flag allows for serialized testing with test.sh
        global ENABLE_AUTHENTICATION
        qrbug.DB_FILE_PATH = Path('TESTS/test_server_db.conf')
        qrbug.INCIDENTS_FILE_PATH = Path('TESTS/test_server_incidents.conf')
        ENABLE_AUTHENTICATION = False
        args.remove('--test')

    host = 'localhost'
    port = 8080
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

    # Loads the config
    qrbug.load_config()
    qrbug.load_incidents()

    # Creates the server
    app = web.Application()
    app.add_routes([
        web.get('/thing={thing_id}', show_failures_tree_route),
        web.get('/', register_incident)
    ])
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

if __name__ == "__main__":
    import sys

    if '-h' in sys.argv or '--help' in sys.argv:
        print("Usage: python -m qrbug.server [--test] [HOST] [PORT]")
        print("\n--test : Use the test databases.")
        pass

    server, host, port = init_server(sys.argv)
    web.run_app(server, host=host, port=port)
