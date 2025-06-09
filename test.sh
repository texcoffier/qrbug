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
rm 'TESTS/xxx-incidents.py'

# Launches the server and tests the two routes
python3 src/qrbug/server.py "$LAUNCH_HOST" "$LAUNCH_PORT" --test >/dev/null &
SERVER_PID="$!"

BASE_URL="http://$LAUNCH_HOST:$LAUNCH_PORT"
TESTING_URL_GET="${BASE_URL}/thing=test_thing"
TESTING_URL_REGISTER="${BASE_URL}/?thing-id=test_thing&failure-id=test&is-repaired=0&what=thing"


echo -n "TEST: load failures list of test_thing"
OK='0'
for _ in 1 2 3 4 5 6 7 8 9 10
do
  if [ "$(curl -s -o TESTS/xxx-page-content -w "%{http_code}" "$TESTING_URL_GET")" = 200 ]; then
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
echo -n " -> loaded"
if grep -q 'failureid="test" thingid="test_thing" what="thing"' TESTS/xxx-page-content
then
  echo " -> content OK"
else
  echo " -> content is BAD"
  EXIT_CODE=1
fi


echo -n "TEST: Registered a report : "

if [ "$(curl -s -o TESTS/xxx-page-content -w "%{http_code}" "$TESTING_URL_REGISTER")" = 200 ]
then
  if grep -q "Quelqu'un" TESTS/xxx-page-content
  then
    if [ -e "TESTS/test_server_incidents.conf" ]; then
      echo "OK"
    else
      echo "FAIL"
      EXIT_CODE=2
    fi
  else
    echo "content FAIL"
    EXIT_CODE=2
  fi
else
    echo "load FAIL"
    EXIT_CODE=2
fi


# Kills the server
kill $SERVER_PID

# Cleans up
echo -n '' > 'TESTS/test_server_incidents.conf'

# Exits
exit $EXIT_CODE