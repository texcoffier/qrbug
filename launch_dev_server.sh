#!/bin/sh

LAUNCH_HOST="$1"
if [ -z "$1" ]; then
  LAUNCH_HOST="localhost"
fi

LAUNCH_PORT="$2"
if [ -z "$2" ]; then
  LAUNCH_PORT="8080"
fi

#python3 -m aiohttp.web -H "$LAUNCH_HOST" -P "$LAUNCH_PORT" qrbug.server:init_server
adev runserver src/qrbug/server.py --app-factory init_server --host "$LAUNCH_HOST" --port "$LAUNCH_PORT"
