from typing import Optional

import qrcode
from aiohttp import web

import qrbug

REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

def run(incident: qrbug.Incident, _request: web.Request) -> Optional[str]:
    url = REPORT_THING_URL.format(incident.thing_id)
    img = qrcode.make(url)
    img.show()
