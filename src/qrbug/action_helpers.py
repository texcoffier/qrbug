from typing import Optional

from aiohttp import web

import qrbug


class ActionReturnValue:
    """
    What is returned by an action.
    """
    def __init__(self, error_msg: str = '', info_msg: str = ''):
        self.error_msg = error_msg
        self.info_msg = info_msg

    def is_empty(self):
        return self.error_msg == '' and self.info_msg == ''

    def __bool__(self):
        return not self.is_empty()


class Request(web.Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response: Optional[web.StreamResponse] = None
        self.ticket: Optional[str] = None

    async def write(self, text: str):
        """ Streams the given text to the web page """
        await self.response.write(text.encode('utf-8'))

    async def write_newline(self, *text: str):
        """ Streams the given text to the web page, and places a newline between each element """
        await self.write('\n'.join(text))

def get_template():
    """The file containing JS helpers and style."""
    return qrbug.REPORT_FAILURE_TEMPLATE.read_text()

qrbug.get_template = get_template
qrbug.Request = Request