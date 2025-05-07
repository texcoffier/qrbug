"""
Contains the code related to loading the journals
"""
import os
from pathlib import Path
from typing import Callable

# Journal files
JOURNALS_FILE_PATH = "JOURNALS/"
DB_FILE_PATH = os.path.join(JOURNALS_FILE_PATH, "db.py")
FAILURES_FILE_PATH = os.path.join(JOURNALS_FILE_PATH, "incidents.py")


def exec_code_file(path: str, code_globals: dict[str, Callable]) -> None:
    with open(path, 'r', encoding='utf-8') as f:
        file_contents = f.read()
    file_code = compile(file_contents, path, 'exec')
    exec(file_code, code_globals)

def get_testing_db_path(test_name: str) -> str:
    """
    Returns the path to the test database file, for the current file.
    :param test_name: The built-in variable `__file__` where this function is called.
    """
    return str(Path(test_name).with_suffix('')) + "_db.conf"
