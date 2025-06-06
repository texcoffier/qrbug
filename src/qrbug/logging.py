import time
from pathlib import Path
import os
from typing import Union

import qrbug


def log(log_folder_path: Path, log_file_prefix: str, content: Union[str, bytes]):
    """
    Logs the given content to a log file.
    """
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S")
    filename = log_folder_path / f'{log_file_prefix}-{current_time}.log'
    attempts_count = 1
    while os.path.exists(filename):
        filename = log_folder_path / f'{log_file_prefix}-{current_time} ({attempts_count + 1}).log'
        attempts_count += 1

    if isinstance(content, bytes):
        params = {'mode': 'wb'}
    else:
        params = {'mode': 'w', 'encoding':'utf-8'}
    with open(filename, **params) as f:
        f.write(content)


qrbug.log = log
