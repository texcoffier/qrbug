"""
Contains the code related to loading the journals
"""
from pathlib import Path
from typing import Callable

# Journal files
JOURNALS_FILE_PATH = Path("JOURNALS")
DB_FILE_PATH = JOURNALS_FILE_PATH / "db.py"
INCIDENTS_FILE_PATH = JOURNALS_FILE_PATH / "incidents.py"


def set_db_path(path: Path) -> None:
    global DB_FILE_PATH
    DB_FILE_PATH = path


def set_incidents_path(path: Path) -> None:
    global INCIDENTS_FILE_PATH
    INCIDENTS_FILE_PATH = path


def exec_code_file(path: Path, code_globals: dict[str, Callable]) -> dict:
    changed_locals = {}
    exec(compile(path.read_text('utf-8'), path, 'exec'), code_globals, changed_locals)
    return changed_locals


def load_config(db_config_path: Path = None) -> None:
    import qrbug

    # Creates default elements
    # These are defined here so they can be overridden by the config
    # The rest of the code assumes these are defined, so they must not be removed !
    qrbug.action('none', 'none.py')
    qrbug.selector('true', 'True')
    qrbug.User.get('nobody')
    qrbug.failure_update('debug', value="Toutes les failures", ask_confirm=False)
    qrbug.thing_update('debug', failure_id="debug", comment="Every available failure")

    # Loads the DB
    exec_code_file(db_config_path if db_config_path is not None else DB_FILE_PATH, qrbug.CONFIGS)

    # Parents every failure WITHOUT PARENTS to the debug failure
    for failure_id, failure in qrbug.Failure.instances.items():
        if failure_id != 'debug' and len(failure.parent_ids) == 0:
            qrbug.failure_add('debug', failure_id)


def load_incidents(incidents_config_path: Path = None) -> None:
    import qrbug
    exec_code_file(incidents_config_path if incidents_config_path is not None else INCIDENTS_FILE_PATH, {
        "incident": qrbug.incident,
        "incident_del": qrbug.incident_del,
        "dispatch": qrbug.dispatch,
    })
