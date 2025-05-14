#!/bin/sh
# Runs the normal tests
python3 -m unittest

# Preps the DB
echo -n '' > 'TESTS/test_server_incidents.conf'

# Launches the server and tests the two routes
python3 src/qrbug/server.py --test >/dev/null &
SERVER_PID="$!"
sleep 1  # Required delay because of server startup time

# Tests that you can load the page for a thing
EXIT_CODE=0
STATUS_CODE="$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8080/thing=test_thing")"
echo "TEST: Access to failures list of test_thing returned HTTP code ${STATUS_CODE}"
if [ "$STATUS_CODE" -ne 200 ]; then
  EXIT_CODE=1
fi

# Tests that you can register a failure
curl -s -o /dev/null -w "" "http://127.0.0.1:8080/?thing-id=test_thing&failure-id=test&is-repaired=0"
if [ -z "$(cat "TESTS/test_server_incidents.conf")" ]; then
  echo "TEST: Failed to register the incident"
  EXIT_CODE=2
else
  echo "TEST: Registered incident"
fi

# Kills the server
kill $SERVER_PID

# Cleans up
echo -n '' > 'TESTS/test_server_incidents.conf'

# Exits
exit $EXIT_CODE