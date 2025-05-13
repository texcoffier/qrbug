"""
Contains the code related to loading the journals
"""
from pathlib import Path
from typing import Callable

# Journal files
JOURNALS_FILE_PATH = Path("JOURNALS")
DB_FILE_PATH = JOURNALS_FILE_PATH / "db.py"
INCIDENTS_FILE_PATH = JOURNALS_FILE_PATH / "incidents.py"


def exec_code_file(path: Path, code_globals: dict[str, Callable]) -> None:
    exec(compile(path.read_text('utf-8'), path, 'exec'), code_globals)
