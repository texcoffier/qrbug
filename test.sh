#!/bin/sh

if [ "$1" = '-h' -o "$1" = '--help' ]; then
  echo "./test.sh [HOST=127.0.0.1] [PORT=8080]"
  exit 0
fi

. .venv/bin/activate

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
mv 'TESTS/xxx-incidents.py' 'TESTS/xxx-incidents-unittest.py'

# Launches the server and tests the two routes
python3 src/qrbug/server.py "$LAUNCH_HOST" "$LAUNCH_PORT" --test >TESTS/xxx-server.log 2>&1 &
SERVER_PID="$!"

BASE_URL="http://$LAUNCH_HOST:$LAUNCH_PORT"
TESTING_URL_GET="${BASE_URL}/thing=test_thing"
TESTING_URL_REGISTER="${BASE_URL}/?thing-id=test_thing&failure-id=test"
TESTING_URL_CLOSE="${BASE_URL}/?thing-id=test_thing&failure-id=test&is-repaired=1"

EXIT_CODE='0'

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
    if [ -e "TESTS/xxx-incidents.py" ]; then
      echo "OK"
    else
      echo "FAIL"
      EXIT_CODE=2
    fi
  else
    echo "content FAIL :"
    echo '---------------------'
    cat TESTS/xxx-page-content
    echo '---------------------'
    EXIT_CODE=3
  fi
else
    echo "load FAIL"
    EXIT_CODE=4
fi

echo -n "TEST: Close incident : "
if [ "$(curl -s -o TESTS/xxx-page-content -w "%{http_code}" "$TESTING_URL_CLOSE")" = 200 ]
then
  if grep -q "👍" TESTS/xxx-page-content
  then
    if grep -q "incident_del('test_thing', 'test'" TESTS/xxx-incidents.py ; then
      echo "OK"
    else
      echo "FAIL"
      EXIT_CODE=5
    fi
  else
    echo "content FAIL"
    EXIT_CODE=6
  fi
else
    echo "load FAIL"
    EXIT_CODE=7
fi


# Kills the server
kill $SERVER_PID

if [ "$EXIT_CODE" != '0' ]
then
  echo "
  ############################################# EXIT_CODE=$EXIT_CODE
  The test failed, here is the server output:
  "
  cat TESTS/xxx-server.log
fi >&2

# Exits
exit $EXIT_CODE