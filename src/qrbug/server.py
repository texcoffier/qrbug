import asyncio
from typing import Optional

from aiohttp import web

from qrbug.thing import Thing
from qrbug.failure import Failure
from qrbug.main import load_config, load_incidents


def get_failures(thing_id: str) -> str:
    requested_thing = Thing.get_if_exists(thing_id)
    if requested_thing is None:
        return "Requested thing not found"

    # Gets the failure for this thing
    current_thing_root_failure = Failure.get_if_exists(requested_thing.failure_id)
    if current_thing_root_failure is None:
        return "Requested thing's root failure not found"

    return current_thing_root_failure.get_hierarchy_representation()


async def show_failures_tree_route(request: web.Request) -> web.Response:
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing: Optional[Thing] = Thing.get_if_exists(thing_id)
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")
    return web.Response(status=200, text=f"Thing ID: {thing_id}\n\n{requested_thing.dump()}\n\nFailures list :\n{get_failures(thing_id)}")


def init_server(argv = None) -> web.Application:
    if argv is None:
        argv = []

    # Loads the configs
    load_config()
    load_incidents()

    # Creates the server
    app = web.Application()
    app.add_routes([web.get('/{thing_id}', show_failures_tree_route)])
    return app

if __name__ == "__main__":
    server = init_server()
    web.run_app(server)
