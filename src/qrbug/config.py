from pathlib import Path

import qrbug


# SETTINGS
TOKEN_LOGIN_TIMEOUT = 600
CAS_URL = 'https://cas.univ-lyon1.fr/cas'
SERVICE_URL = 'http://qrbug.univ-lyon1.fr:8080'
HOST = 'localhost'
PORT = 8080
SMTP_SERVER = ['smtp1.your.domain', 'smtp2.your.domain']
SMTP_DEFAULT_SENDER = 'do-not-reply@nowhere.in.the.world'
LDAP_SERVER = 'ldaps:ldap.your.domain'
LDAP_LOGIN = 'admin_login'
LDAP_PASSWORD = 'admin_password'
LDAP_DC = 'DC=your,DC=domain'
LDAP_ID = 'sAMAccountName'
DEFAULT_EMAIL_TO = 'an-administrator@your.domain' # if recipient without email
LOG_FORMAT = '%Y%m%d%H%M%S'  # The format for the log files
LOG_FILE_EXTENSION = ''

try:
    from qrbug.settings import *
except ModuleNotFoundError:
    print("«src/qrbug/settings.py» not found, use default values")
print()
print(f"TOKEN_LOGIN_TIMEOUT: {TOKEN_LOGIN_TIMEOUT}")
print(f"            CAS_URL: {CAS_URL}")
print(f"        SERVICE_URL: {SERVICE_URL}")
print(f"               HOST: {HOST}")
print(f"               PORT: {PORT}")
print(f"        SMTP_SERVER: {SMTP_SERVER}")
print(f"SMTP_DEFAULT_SENDER: {SMTP_DEFAULT_SENDER}")
print(f"   DEFAULT_EMAIL_TO: {DEFAULT_EMAIL_TO}")
print(f"        LDAP_SERVER: {LDAP_SERVER}")
print(f"         LDAP_LOGIN: {LDAP_LOGIN}")
print(f"      LDAP_PASSWORD: {LDAP_PASSWORD}")
print(f"            LDAP_DC: {LDAP_DC}")
print(f"            LDAP_ID: {LDAP_ID}")


SERVICE_URL = SERVICE_URL.rstrip('/')

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

# Directories
ACTIONS_FOLDER = Path('ACTIONS')

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
    "Checkbox"         : qrbug.DisplayTypes.checkbox,
    "Datalist"         : qrbug.DisplayTypes.datalist,
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

qrbug.CONFIGS = CONFIGS
qrbug.INCIDENT_FUNCTIONS = INCIDENT_FUNCTIONS

qrbug.HOST = HOST
qrbug.PORT = PORT
qrbug.SMTP_SERVER = SMTP_SERVER
qrbug.SMTP_DEFAULT_SENDER = SMTP_DEFAULT_SENDER
qrbug.DEFAULT_EMAIL_TO = DEFAULT_EMAIL_TO
qrbug.ACTIONS_FOLDER = ACTIONS_FOLDER
qrbug.LDAP_SERVER = LDAP_SERVER
qrbug.LDAP_LOGIN = LDAP_LOGIN
qrbug.LDAP_PASSWORD = LDAP_PASSWORD
qrbug.LDAP_DC = LDAP_DC
qrbug.LDAP_ID = LDAP_ID
qrbug.LOG_FORMAT = LOG_FORMAT
qrbug.LOG_FILE_EXTENSION = LOG_FILE_EXTENSION
