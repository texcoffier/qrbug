#!/bin/sh

set -e  # Stops on error

if [ "" = "$1" ]
then
    echo "The first argument is the login to the server to configure"
    echo "For example: qrbug@demo710.univ-lyon1.fr"
    echo "If they are other arguments they indicates function to launch"
    exit 1
fi >&2

H=$1
shift

copy() {
    echo "==== QRBUG ==== Copy local source files even if not commited"
    tar -cf - $(git ls-files) | ssh "$H" "tar -xf -"
}

configure() {
    echo -e "==== QRBUG ==== Configuration "
    python3 src/qrbug/config.py |
    ssh "$H" "
        if [ -e src/qrbug/settings.py ]
            then
                echo 'is in remote «src/qrbug/settings.py»'
            else
                echo 'must be edited in «src/qrbug/settings.py»'
                cat >src/qrbug/settings.py
                exit 1
            fi
            "
}

create_venv() {
    echo "==== QRBUG ==== Create virtual envs"
    ssh "$H" "./install.sh | (head --line 1 ; tail --line 2)"
}

kill_server_and_test() {
    echo -n "==== QRBUG ==== QRBUG "
    ssh "$H" "
        . .venv/bin/activate
        PORT=\$( (cat src/qrbug/settings.py ; echo 'print(PORT)') | python3)
        # Kill server if port open
        netcat -zv 127.0.0.1 \$PORT 2>/dev/null &&
            pkill --oldest -u \$(id -u) -f server.py &&
                echo 'has been killed' || echo 'is not running'
        echo -n '==== QRBUG ==== Regression tests: '
        if ./test.sh localhost \$PORT >TESTS/xxx.errors 2>&1
        then
            echo "OK"
        else
            echo "FAIL"
            cat TESTS/xxx.errors
            exit 1
        fi
    "
}

start() {
    echo "==== QRBUG ==== Run QRBUG"
    ssh "$H" "
        . .venv/bin/activate
        nohup python3 src/qrbug/server.py >xxx.log 2>&1 </dev/null &
        sleep 1"
}

echo "==== QRBUG ==== Destination host: $H"
if [ "" = "$1" ]
then
    TO_RUN="copy configure create_venv kill_server_and_test start"
else
    TO_RUN="$@"
fi
echo "==== QRBUG ==== Functions to run: $TO_RUN"
for I in $TO_RUN
    do
        eval $I
    done
echo "==== QRBUG ==== Done"
