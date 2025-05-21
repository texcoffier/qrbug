"""
An empty action : Does nothing.
"""
from typing import Optional
from aiohttp import web

import qrbug

def run(_incident: qrbug.Incidents, _request: web.Request) -> Optional[str]:
    pass