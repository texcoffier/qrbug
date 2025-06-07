from pathlib import Path
import asyncio
import html
from typing import Optional, List
from aiohttp import web
import qrbug

FILENAME = {
    'journal-config': qrbug.DB_FILE_PATH,
    'journal-default': qrbug.DEFAULT_DB_PATH,
    'journal-incident': qrbug.INCIDENTS_FILE_PATH,
}

async def run(incidents: List[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]
    FILE_CHUNK_SIZE_BYTES = 100_000

    async def stream_html_from_path(path: Path, stream):
        with open(path, 'r', encoding='utf-8') as f:
            while True:
                text = f.read(FILE_CHUNK_SIZE_BYTES)
                if not text:
                    break
                await stream.write(
                    html.escape(text).encode('utf-8')
                )
                await asyncio.sleep(0)

    await request.response.write(
        b'<style>pre { font-family: monospace, monospace; background: #FFC; }</style>\n\n'
    )
    await request.response.write(f'<h2>{qrbug.Failure.instances[incident.failure_id].value} :</h2><pre>'.encode('utf-8'))
    await stream_html_from_path(FILENAME[incident.failure_id], request.response)
    await request.response.write('</pre>\n'.encode('utf-8'))

    return None
