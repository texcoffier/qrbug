import asyncio
import datetime
import time
from datetime import datetime
from typing import Optional

from aiohttp import web

from qrbug.thing import Thing
from qrbug.failure import Failure
from qrbug.main import load_config, load_incidents, INCIDENTS_FILE_PATH


def get_failures(thing_id: str, as_html: bool = True) -> str:
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
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing: Optional[Thing] = Thing.get_if_exists(thing_id)
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")
    #return web.Response(status=200, text=f"Thing ID: {thing_id}\n\n{requested_thing.dump()}\n\nFailures list :\n{get_failures(thing_id)}")
    return web.Response(status=200, text=get_failures(thing_id), content_type='text/html')


async def register_incident(request: web.Request) -> web.Response:
    thing_id: Optional[str] = request.rel_url.query.get("thing-id", None)
    failure_id: Optional[str] = request.rel_url.query.get("failure-id", None)
    is_repaired: Optional[str] = request.rel_url.query.get("is-repaired", None)
    additional_info: Optional[str] = request.rel_url.query.get("additional-info", None)

    valid_request = all((e is not None for e in (thing_id, failure_id, is_repaired)))
    # TODO: Do better.
    if valid_request is False:
        missing_params = []
        if thing_id is None:
            missing_params.append("thing_id")
        if failure_id is None:
            missing_params.append("failure_id")
        if is_repaired is None:
            missing_params.append("is_repaired")
        return web.Response(status=404, text=f"Missing query parameters : " + ", ".join(missing_params))

    is_repaired_bool: bool = is_repaired == '1'
    timestamp = int(time.time())
    current_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    function_name = "incident_del" if is_repaired_bool else "incident"
    user_ip = request.remote

    # TODO: ESCAPE ALL SINGLE QUOTES !
    function_to_log = f"{function_name}('{thing_id}', '{failure_id}', '{user_ip}', {timestamp}"
    if additional_info is not None and is_repaired_bool is False:
        # incident_del() does not take additional_info as parameter,
        # therefore if the incident is repaired, we must ABSOLUTELY NOT get into this if block
        function_to_log += f", '{additional_info}'"
    function_to_log += f")  # {current_date} TODO LOGIN\n"

    with open(INCIDENTS_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write(function_to_log)

    return_string = (f"thing_id={thing_id}\n"
                     f"failure_id={failure_id}\n"
                     f"is_repaired={is_repaired_bool}\n"
                     f"additional_info={additional_info}\n\n"
                     f"valid_request={valid_request}\n\n"
                     f"Registered new incident.")
    return web.Response(status=200, text=return_string)



def init_server(argv = None) -> web.Application:
    if argv is None:
        argv = []

    # Loads the configs
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
    server = init_server()
    web.run_app(server)
