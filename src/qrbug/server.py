import asyncio
import datetime
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiohttp import web

from qrbug.thing import Thing
from qrbug.failure import Failure
from qrbug.journals import load_config, load_incidents, set_db_path, set_incidents_path
import qrbug.journals


def get_failures(thing_id: str, as_html: bool = True) -> str:
    """
    Returns the representation of the failure of the given thing, as HTML or raw text.
    :param thing_id: The id of the thing.
    :param as_html: If True, return an HTML representation of the failure. Otherwise, returns as raw text.
    """
    requested_thing = Thing.get_if_exists(thing_id)
    if requested_thing is None:
        return "Requested thing not found"

    # Gets the failure for this thing
    current_thing_root_failure = Failure.get_if_exists(requested_thing.failure_id)
    if current_thing_root_failure is None:
        return "Requested thing's root failure not found"

    if as_html:
        return current_thing_root_failure.get_hierarchy_representation_html(thing_id)
    else:
        return current_thing_root_failure.get_hierarchy_representation()


async def show_failures_tree_route(request: web.Request) -> web.Response:
    """
    Returns the webpage listing the failure hierarchy for the given thing.
    """
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing: Optional[Thing] = Thing.get_if_exists(thing_id)
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")
    #return web.Response(status=200, text=f"Thing ID: {thing_id}\n\n{requested_thing.dump()}\n\nFailures list :\n{get_failures(thing_id)}")
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
    function_to_log += f")  # {current_date} TODO LOGIN\n"

    with open(qrbug.journals.INCIDENTS_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(function_to_log)

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



def init_server(argv = None) -> web.Application:
    """
    Function that will be run on server startup.
    Loads the config and incidents journals, starts a new server, and creates the routes.
    """
    if argv is None:
        argv = []

    if '--test' in argv:
        set_db_path(Path('TESTS/test_server_db.conf'))
        set_incidents_path(Path('TESTS/test_server_incidents.conf'))

    # Loads the config
    load_config()
    load_incidents()

    # Creates the server
    app = web.Application()
    app.add_routes([
        web.get('/thing={thing_id}', show_failures_tree_route),
        web.get('/', register_incident)
    ])
    return app

if __name__ == "__main__":
    import sys

    if '-h' in sys.argv or '--help' in sys.argv:
        print("Usage: python -m qrbug.server [HOST] [PORT] [--test]")
        print("\n--test : Use the test databases.")
        pass

    server = init_server(sys.argv)
    HOST = 'localhost'
    PORT = 8080
    if len(sys.argv) >= 2:
        HOST = sys.argv[1]
    if len(sys.argv) >= 3:
        PORT = int(sys.argv[2])
    web.run_app(server, host=HOST, port=PORT)
