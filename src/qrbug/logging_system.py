import time
from pathlib import Path
import os
from typing import Union

import qrbug

def log(log_folder_path: Path, content: Union[str, bytes], log_prefix: str = ''):
    """
    Logs the given content to a log file.
    """
    log_format = qrbug.LOG_FORMAT
    if log_prefix:
        log_format = log_format.format(prefix=f'{log_prefix}-')
    current_time = time.strftime(log_format)
    filename = log_folder_path / current_time
    attempts_count = 1
    while os.path.exists(filename):
        attempts_count += 1
        filename = log_folder_path / f'{current_time}-{attempts_count}'

    if isinstance(content, bytes):
        filename.write_bytes(content)
    else:
        filename.write_text(content, encoding='utf-8')

def log_email(content: bytes):
    return log(qrbug.EMAIL_LOG_DIRECTORY, content, 'mail')

def log_error(content: str):
    return log(qrbug.ERROR_LOG_DIRECTORY, content, 'backtrace')

qrbug.log = log
qrbug.log_email = log_email
qrbug.log_error = log_error
