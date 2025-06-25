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

def get_template(request=None, datalists_to_load=tuple(), force_load:bool=False):
    """The file containing JS helpers and style."""
    if force_load or get_template._template_last_modified_timestamp != qrbug.REPORT_FAILURE_TEMPLATE.stat().st_mtime:
        template = qrbug.REPORT_FAILURE_TEMPLATE.read_text()
        get_template._template_last_modified_timestamp = qrbug.REPORT_FAILURE_TEMPLATE.stat().st_mtime
        get_template._template_cached_string = template
    else:
        template = get_template._template_cached_string

    if request:
        template += f'<script>var secret="{request.secret.secret}";</script>'

    datalist_text = []
    for datatype in datalists_to_load:
        datalist_text.append(f'<datalist id="datalist_{datatype}">')
        if datatype == "ActionScripts":
            for file in qrbug.ACTIONS_FOLDER.glob('*.py'):
                datalist_text.append(f'<option>{file.name}</option>')
        else:
            cls = getattr(qrbug, datatype)
            for instance in cls.instances:
                datalist_text.append(f'<option>{instance}</option>')
        datalist_text.append(f'</datalist>')

    return template.replace('%DATALISTS%', ''.join(datalist_text))

qrbug.get_template = get_template
qrbug.Request = Request