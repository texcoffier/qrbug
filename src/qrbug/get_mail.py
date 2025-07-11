"""
Get mail from login
"""
import asyncio
import queue
import threading
import time
import ldap
import traceback
import re
import qrbug

def safe(txt):
    return re.sub('[^-a-zA-Z0-9_.]', '_', txt)

QUEUE = queue.Queue()
MAILS = {}

def thread_mail():
    while not hasattr(qrbug, 'LDAP_ID'):
        time.sleep(0.1)
    while True:
        session = ldap.ldapobject.ReconnectLDAPObject(
            qrbug.LDAP_SERVER,
            retry_max=10,
            retry_delay=5.,
            trace_stack_limit=0)
        session.set_option(ldap.OPT_TIMELIMIT, 10)
        session.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        session.set_option(ldap.OPT_REFERRALS, 0)
        session.set_option(ldap.OPT_X_KEEPALIVE_IDLE, True)
        session.simple_bind_s(qrbug.LDAP_LOGIN, qrbug.LDAP_PASSWORD)
        try:
            while True:
                login = QUEUE.get()
                infos = session.search_s(
                    qrbug.LDAP_DC, ldap.SCOPE_SUBTREE,
                    f'({qrbug.LDAP_ID}={safe(login)})', ('mail',))
                for i in infos:
                    if i[0]:
                        MAILS[login] = i[1]['mail'][0].decode('utf-8')
                        break
                else:
                    MAILS[login] = qrbug.DEFAULT_EMAIL_TO
        except ValueError:
            qrbug.Incident.open('GUI', 'backtrace', '', 'system', '\n'.join(traceback.format_exc()))

MAILS_THREAD = threading.Thread(target=thread_mail, daemon=True)
MAILS_THREAD.start()

async def get_mail_from_login(login):
    if login in MAILS:
        return MAILS[login]
    QUEUE.put(login)
    for _ in range(1000):
        if login in MAILS:
            return MAILS[login]
        await asyncio.sleep(0.01)
    return qrbug.DEFAULT_EMAIL_TO

qrbug.get_mail_from_login = get_mail_from_login
