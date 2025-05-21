"""
Contains the code related to loading the journals
"""
from pathlib import Path
from typing import Callable
import enum


class Journals(enum.Enum):
    DB = enum.auto()
    INCIDENTS = enum.auto()
    DEFAULT_DB = enum.auto()


def exec_code_file(path: Path, code_globals: dict[str, Callable]) -> dict:
    changed_locals = {}
    exec(compile(path.read_text('utf-8'), path, 'exec'), code_globals, changed_locals)
    return changed_locals


def load_config(db_config_path: Path = None, default_db_path: Path = None) -> None:
    import qrbug

    # Loads the default DB
    exec_code_file(default_db_path if default_db_path is not None else qrbug.DEFAULT_DB_PATH, qrbug.CONFIGS)

    # Loads the DB
    exec_code_file(db_config_path if db_config_path is not None else qrbug.DB_FILE_PATH, qrbug.CONFIGS)

    # Parents every failure WITHOUT PARENTS to the debug failure
    for failure_id, failure in qrbug.Failure.instances.items():
        if failure_id != 'debug' and len(failure.parent_ids) == 0:
            qrbug.failure_add('debug', failure_id)


def load_incidents(incidents_config_path: Path = None) -> None:
    import qrbug
    exec_code_file(
        incidents_config_path if incidents_config_path is not None else qrbug.INCIDENTS_FILE_PATH,
        qrbug.INCIDENT_FUNCTIONS
    )


def append_line_to_journal(line: str, journal: Journals = Journals.INCIDENTS) -> "Incident":
    """
    Adds a new line at the end of the given journal and executes it in the current environment.
    """
    import qrbug

    if journal == Journals.INCIDENTS:
        journal_path = qrbug.INCIDENTS_FILE_PATH
        given_globals = qrbug.INCIDENT_FUNCTIONS
    elif journal == Journals.DB:
        journal_path = qrbug.DB_FILE_PATH
        given_globals = qrbug.CONFIGS
    elif journal == Journals.DEFAULT_DB:
        journal_path = qrbug.DEFAULT_DB_PATH
        given_globals = qrbug.CONFIGS
    else:
        raise ValueError(f"Unknown journal {journal}")

    with open(journal_path, 'a', encoding='utf-8') as f:
        f.write(line)

    line_vars = {}
    exec(compile('current_incident = ' + line, 'no file', 'exec'), given_globals, line_vars)
    return line_vars['current_incident']
