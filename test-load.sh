#!/bin/sh

# 50MB RAM for a config with 10000 objects

. .venv/bin/activate

PROFILE="--profile"
PROFILE=

echo "Create big journals"
./test-load.py # Create big config journal an incident journal
ls -ls TESTS/xxx-testload.conf TESTS/xxx-incidents.py

echo "Start server. WAIT A MINUTE."
python3 src/qrbug/server.py "localhost" "8080" --test --testload $PROFILE >TESTS/xxx-load-server.log 2>&1 &
QRBUG_PID=$!
trap "kill $QRBUG_PID" 0 # Kill server on exit

START=$(date "+%s")
OK='0'
for _ in $(seq 10000)
do
  if [ "$(curl -s -o TESTS/xxx-page-content -w "%{http_code}" "http://localhost:8080/?what=thing&thing-id=GUI&failure-id=stats")" = 200 ]; then
    OK='1'
    break
  else
    sleep 1
  fi
done
if [ "$OK" = '0' ]; then
  echo "src/qrbug/server.py cannot be started"
  exit 1
fi
echo "Server running after $(expr $(date '+%s') - $START) seconds"
ps -fle | grep -e UID -e $QRBUG_PID

echo "Profiling information in : TESTS/xxx-load-server.log"

if grep -q '0 tickets sans retour' TESTS/xxx-page-content
then
  echo " -> content OK"
else
  echo " -> content is BAD, current content is in TESTS/xxx-page-content"
  EXIT_CODE=1
fi

kill $QRBUG_PID
