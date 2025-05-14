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
    qrbug.main.action('none', 'none.py')
    qrbug.main.selector('true', 'True')
    exec_code_file(db_config_path if db_config_path is not None else DB_FILE_PATH, qrbug.main.CONFIGS)


def load_incidents(incidents_config_path: Path = None) -> None:
    import qrbug
    exec_code_file(incidents_config_path if incidents_config_path is not None else INCIDENTS_FILE_PATH, {
        "incident": qrbug.main.incident,
        "incident_del": qrbug.main.incident_del,
        "dispatch": qrbug.main.dispatch,
    })
