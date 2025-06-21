#!/bin/sh

H='qrbug@demo710.univ-lyon1.fr'
S='https://demo710.univ-lyon1.fr/QRBUG/'

echo "==== QRBUG ==== Destination host: $H"

echo "==== QRBUG ==== Copy local source files even if not commited:"
tar -cf - $(git ls-files) | ssh "$H" "tar -xf -"

echo "==== QRBUG ==== Configure QRBUG"
if [ -e $H.py ]
then
    cat $H.py | ssh "$H" "cat >src/qrbug/settings.py"
else
    echo "
TOKEN_LOGIN_TIMEOUT = 86400
PORT = 8099
SERVICE_URL = 'https://qrbug.your.domain/'
QRBUG_SMTP_SERVER = ['smtp1.your.domain', 'smtp2.your.domain']
QRBUG_SMTP_DEFAULT_SENDER = 'do-not-reply@nowhere.in.the.world'
" >$H.py
    echo "==== QRBUG ==== Missing remote configuration, you must edit:"
    echo "==== QRBUG ====     $H.py"
    echo "==== QRBUG ==== Once it is done, restart the script."
    exit 1
fi

echo "==== QRBUG ==== Create virtual envs"
ssh "$H" "./install.sh | (head --line 1 ; tail --line 2)"

echo "==== QRBUG ==== Test QRBUG"
ssh "$H" "./test.sh"

echo "==== QRBUG ==== Run QRBUG"
ssh "$H" ". .venv/bin/activate ; python3 src/qrbug/server.py"
