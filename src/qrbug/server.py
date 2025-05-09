import sys

from aiohttp import web
import asyncio
from typing import Optional

from qrbug.thing import Thing
from qrbug.main import load_config, load_incidents


async def show_failures_tree_route(request: web.Request) -> web.Response:
    thing_id: Optional[str] = request.match_info.get('thing_id', None)
    if thing_id is None:
        return web.Response(status=404, text="No thing ID provided")
    requested_thing: Optional[Thing] = Thing.get_if_exists(thing_id)
    if requested_thing is None:
        return web.Response(status=404, text="Requested Thing does not exist")
    return web.Response(status=200, text=f"Thing ID: {thing_id}\n\n{requested_thing.dump()}")


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
