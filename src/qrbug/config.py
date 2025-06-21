from pathlib import Path

import qrbug


# SETTINGS
TOKEN_LOGIN_TIMEOUT = 60
CAS_URL = 'https://cas.univ-lyon1.fr/cas'
SERVICE_URL = 'http://qrbug.univ-lyon1.fr:8080/'
HOST = 'localhost'
PORT = 8080

try:
    from settings import *
except ModuleNotFoundError:
    print("«src/qrbug/settings.py» not found, use default values")
print(f"TOKEN_LOGIN_TIMEOUT: {TOKEN_LOGIN_TIMEOUT}")
print(f"            CAS_URL: {CAS_URL}")
print(f"        SERVICE_URL: {SERVICE_URL}")
print(f"               HOST: {HOST}")
print(f"               PORT: {PORT}")

# Journal files
JOURNALS_FILE_PATH = Path("JOURNALS")
DB_FILE_PATH = JOURNALS_FILE_PATH / "db.py"
DEFAULT_DB_PATH = JOURNALS_FILE_PATH / "default_db.py"
INCIDENTS_FILE_PATH = JOURNALS_FILE_PATH / "incidents.py"

# Template files
STATIC_FILES_PATH = Path('STATIC')
FAVICON_PATH = STATIC_FILES_PATH / 'favicon.ico'
REPORT_FAILURE_TEMPLATE = STATIC_FILES_PATH / 'report_failure.html'

# Logging
LOG_DIRECTORY = Path('LOGS')
EMAIL_LOG_DIRECTORY = LOG_DIRECTORY / 'MAIL'
ERROR_LOG_DIRECTORY = LOG_DIRECTORY / 'ERROR'
EMAIL_LOG_PREFIX = 'mail'
ERROR_LOG_PREFIX = 'backtrace'

# Dicts
CONFIGS = {
    "user_update"      : qrbug.user_update,
    "user_add"         : qrbug.user_add,
    "user_remove"      : qrbug.user_remove,
    "failure_update"   : qrbug.failure_update,
    "failure_add"      : qrbug.failure_add,
    "failure_remove"   : qrbug.failure_remove,
    "DisplayTypes"     : qrbug.DisplayTypes, # DEPRECATED
    "Text"             : qrbug.DisplayTypes.text,
    "Button"           : qrbug.DisplayTypes.button,
    "Redirect"         : qrbug.DisplayTypes.redirect,
    "Textarea"         : qrbug.DisplayTypes.textarea,
    "Input"            : qrbug.DisplayTypes.input,
    "Boolean"          : qrbug.DisplayTypes.boolean,
    "Display"          : qrbug.DisplayTypes.display,
    "thing_update"     : qrbug.thing_update,
    "thing_del"        : qrbug.thing_del,
    "thing_remove"     : qrbug.thing_remove,
    "thing_add"        : qrbug.thing_add,
    "thing_add_failure": qrbug.thing_add_failure,
    "thing_del_failure": qrbug.thing_del_failure,
    "action"           : qrbug.action_update,
    "selector"         : qrbug.selector_update,
    "dispatcher_update": qrbug.dispatcher_update,
    "dispatcher_del"   : qrbug.dispatcher_del,
    "concerned_add"    : qrbug.concerned_add,
    "concerned_del"    : qrbug.concerned_del,
}

INCIDENT_FUNCTIONS = {
    "incident_new": qrbug.incident_new,
    "incident_del": qrbug.incident_del,
    "dispatch"    : qrbug.dispatch,
}


# Exports those variables
qrbug.TOKEN_LOGIN_TIMEOUT = TOKEN_LOGIN_TIMEOUT
qrbug.CAS_URL = CAS_URL
qrbug.SERVICE_URL = SERVICE_URL
qrbug.JOURNALS_FILE_PATH = JOURNALS_FILE_PATH
qrbug.DB_FILE_PATH = DB_FILE_PATH
qrbug.DEFAULT_DB_PATH = DEFAULT_DB_PATH
qrbug.INCIDENTS_FILE_PATH = INCIDENTS_FILE_PATH
qrbug.STATIC_FILES_PATH = STATIC_FILES_PATH
qrbug.FAVICON_PATH = FAVICON_PATH
qrbug.REPORT_FAILURE_TEMPLATE = REPORT_FAILURE_TEMPLATE
qrbug.LOG_DIRECTORY = LOG_DIRECTORY
qrbug.EMAIL_LOG_DIRECTORY = EMAIL_LOG_DIRECTORY
qrbug.ERROR_LOG_DIRECTORY = ERROR_LOG_DIRECTORY
qrbug.EMAIL_LOG_PREFIX = EMAIL_LOG_PREFIX
qrbug.ERROR_LOG_PREFIX = ERROR_LOG_PREFIX

qrbug.CONFIGS = CONFIGS
qrbug.INCIDENT_FUNCTIONS = INCIDENT_FUNCTIONS

qrbug.HOST = HOST
qrbug.PORT = PORT