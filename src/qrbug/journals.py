"""
Contains the code related to loading the journals
"""
from pathlib import Path
from typing import Callable

# Journal files
JOURNALS_FILE_PATH = Path("JOURNALS")
DB_FILE_PATH = JOURNALS_FILE_PATH / "db.py"
INCIDENTS_FILE_PATH = JOURNALS_FILE_PATH / "incidents.py"


def exec_code_file(path: Path, code_globals: dict[str, Callable]) -> dict:
    changed_locals = {}
    exec(compile(path.read_text('utf-8'), path, 'exec'), code_globals, changed_locals)
    return changed_locals


def load_config() -> None:
    import qrbug
    exec_code_file(DB_FILE_PATH, qrbug.main.CONFIGS)


def load_incidents() -> None:
    import qrbug
    exec_code_file(INCIDENTS_FILE_PATH, {
        "incident": qrbug.main.incident,
        "incident_del": qrbug.main.incident_del,
        "dispatch": qrbug.main.dispatch,
    })
