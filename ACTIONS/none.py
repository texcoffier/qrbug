"""
An empty action : Does nothing.
"""
from typing import Optional, List
from aiohttp import web

import qrbug

def run(_incidents: List[qrbug.Incident], _request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    pass