#!/bin/sh

if [ "$1" = '-h' -o "$1" = '--help' ]; then
  echo "./test.sh [HOST=127.0.0.1] [PORT=8080]"
  exit 0
fi


# Gathers command line arguments
LAUNCH_HOST="$1"
if [ -z "$1" ]; then
  LAUNCH_HOST="localhost"
fi

LAUNCH_PORT="$2"
if [ -z "$2" ]; then
  LAUNCH_PORT="8080"
fi

# Runs the normal tests
python3 -m unittest

# Preps the DB
echo -n '' > 'TESTS/test_server_incidents.conf'

# Launches the server and tests the two routes
python3 src/qrbug/server.py "$LAUNCH_HOST" "$LAUNCH_PORT" --test >/dev/null &
SERVER_PID="$!"

BASE_URL="http://$LAUNCH_HOST:$LAUNCH_PORT"
TESTING_URL_GET="${BASE_URL}/thing=test_thing"
TESTING_URL_REGISTER="${BASE_URL}/?thing-id=test_thing&failure-id=test&is-repaired=0"

# Tests that the server
OK='0'
for _ in 1 2 3 4 5 6 7 8 9 10
do
  if [ "$(curl -s -o /dev/null -w "%{http_code}" "$TESTING_URL_GET")" = 200 ]; then
    OK='1'
    break
  else
    sleep 0.1
  fi
done
if [ "$OK" = '0' ]; then
  echo "src/qrbug/server.py cannot be started"
  exit 1
fi

# Tests that you can load the page for a thing
EXIT_CODE=0
STATUS_CODE="$(curl -s -o /dev/null -w "%{http_code}" "$TESTING_URL_GET")"
echo -n "TEST: Access to failures list of test_thing returned HTTP code ${STATUS_CODE}"
if [ "$STATUS_CODE" -ne 200 ]; then
  echo " -> FAIL"
  EXIT_CODE=1
else
  echo " -> OK"
fi

# Tests that you can register a failure
curl -s -o /dev/null -w "" "$TESTING_URL_REGISTER"
if [ -z "$(cat "TESTS/test_server_incidents.conf")" ]; then
  echo "TEST: Failed to register the incident -> FAIL"
  EXIT_CODE=2
else
  echo "TEST: Registered incident -> OK"
fi

# Kills the server
kill $SERVER_PID

# Cleans up
echo -n '' > 'TESTS/test_server_incidents.conf'

# Exits
exit $EXIT_CODE