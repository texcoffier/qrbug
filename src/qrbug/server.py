import datetime
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiohttp import web

from qrbug.authentication import get_login_from_token, handle_login
from qrbug.dispatcher import Dispatcher
from qrbug.thing import Thing
from qrbug.failure import Failure
from qrbug.journals import load_config, load_incidents, set_db_path, set_incidents_path
from qrbug.incidents import incident, incident_del
import qrbug.journals


def get_failures(thing_id: str, as_html: bool = True) -> str:
    """
    Returns the representation of the failure of the given thing, as HTML or raw text.
    :param thing_id: The id of the thing.
    :param as_html: If True, return an HTML representation of the failure. Otherwise, returns as raw text.
    """
    requested_thing = Thing[thing_id]
    if requested_thing is None:
        return "Requested thing not found"

    # Gets the failure for this thing
    root_failure = Failure[requested_thing.failure_id]
    if root_failure is None:
        return "Requested thing's root failure not found"

    if as_html:
        return root_failure.get_hierarchy_representation_html(thing_id)
    else:
        return root_failure.get_hierarchy_representation()


async def show_failures_tree_route(request: web.Request) -> web.Response:
    """
    Returns the webpage listing the failure hierarchy for the given thing.
    """
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing: Optional[Thing] = Thing[thing_id]
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")

    # Creates the CAS login
    user_login = await handle_login(request, f'thing={thing_id}')
    if user_login is None:
        return web.Response(status=403, text="Login ticket invalid")

    #return web.Response(status=200, text=f"Thing ID: {thing_id}\n\n{requested_thing.dump()}\n\nFailures list :\n{get_failures(thing_id)}")
    # TODO : Groupe autorisé à déclarer la panne
    if thing_id == 'debug':
        return web.Response(status=200, text=get_failures(thing_id, as_html=False))
    return web.Response(status=200, text=get_failures(thing_id), content_type='text/html')


async def register_incident(request: web.Request) -> web.Response:
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
    failure = Failure[failure_id]
    if failure is None:
        return web.Response(status=404, text=f"Failure does not exist")
    if Thing[thing_id] is None:
        return web.Response(status=404, text=f"Thing does not exist")

    # Cas authentication
    user_token = request.query.get("token", None)
    user_login = ''
    # Only authenticate if failure requires it
    if failure.restricted_to_group_id is not None:
        if user_token is not None:
            user_login = get_login_from_token(user_token, request.remote)
        if not user_login:
            user_login = await handle_login(request, f'thing={thing_id}')
            if user_login is None:
                return web.Response(status=403, text="Login ticket invalid")

    is_repaired_bool: bool = is_repaired == '1'
    timestamp = int(time.time())
    current_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    function_name = "incident_del" if is_repaired_bool else "incident"
    user_ip = request.remote

    function_to_log = f"{function_name}({repr(thing_id)}, {repr(failure_id)}, {repr(user_ip)}, {timestamp}"
    if additional_info is not None and is_repaired_bool is False:
        # incident_del() does not take additional_info as parameter,
        # therefore if the incident is repaired, we must ABSOLUTELY NOT get into this if block
        # if this incident is resolved
        function_to_log += f", {repr(additional_info)}"
    function_to_log += f")  # {current_date} {user_login}\n"

    with open(qrbug.journals.INCIDENTS_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(function_to_log)

    if is_repaired_bool:
        incident_del(thing_id, failure_id, user_ip, timestamp)
    else:
        current_incident = incident(thing_id, failure_id, user_ip, timestamp, additional_info)

    # Dispatchers
    if not is_repaired_bool:
        for dispatcher in Dispatcher.instances.values():
            if dispatcher.when == 'synchro':
                dispatcher.run([current_incident], 'nobody')
            else:
                pass # TODO: Rajouter la fonction dispatch au journal d'incidents

    # return_string = (f"thing_id={thing_id}\n"
    #                  f"failure_id={failure_id}\n"
    #                  f"is_repaired={is_repaired_bool}\n"
    #                  f"additional_info={additional_info}\n\n"
    #                  f"valid_request={valid_request}\n\n"
    #                  f"Registered new incident.")
    # return web.Response(status=200, text=return_string)
    return web.Response(
        status=200,
        text="<h1>Merci !</h1><h3>Votre signalement a été enregistré.</h3>",
        content_type='text/html'
    )


def parse_command_line_args(argv) -> tuple[str, int]:
    """
    Parses the command line args and returns them.
    :param argv: The command line args.
    :return: The host and port that should be used by the server.
    """
    args = argv.copy()  # In order not to modify the original args
    if '--test' in args:
        set_db_path(Path('TESTS/test_server_db.conf'))
        set_incidents_path(Path('TESTS/test_server_incidents.conf'))
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

    /!\ RETURNS A web.Application ONLY /!\
    This is required by the server starting framework.
    """
    if argv is None:
        argv = []

    host, port = parse_command_line_args(argv)

    # Loads the config
    load_config()
    load_incidents()

    # Creates the server
    app = web.Application()
    app.add_routes([
        web.get('/thing={thing_id}', show_failures_tree_route),
        web.get('/', register_incident)
    ])
    return app, host, port

def get_server(argv: list = None) -> web.Application:
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
