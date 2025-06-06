import time
from pathlib import Path
import os
from typing import Union

import qrbug


def log(log_folder_name: str, log_file_prefix: str, content: Union[str, bytes]):
    """
    Logs the given content to a log file.
    """
    filename = f'LOGS/{log_folder_name}/{log_file_prefix}-{time.strftime("%Y-%m-%d-%H-%M-%S")}.log'
    attempts_count = 1
    while os.path.exists(filename):
        filename = filename.rstrip('.log').rstrip(f' ({attempts_count})') + f' ({attempts_count + 1}).log'
        attempts_count += 1

    if isinstance(content, bytes):
        params = {'mode': 'wb'}
    else:
        params = {'mode': 'w', 'encoding':'utf-8'}
    with open(filename, **params) as f:
        f.write(content)


qrbug.log = log
