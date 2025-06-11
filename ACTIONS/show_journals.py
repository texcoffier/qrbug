from pathlib import Path
import asyncio
import html
from typing import Optional, List
import qrbug

FILENAME = {
    'journal-config': qrbug.DB_FILE_PATH,
    'journal-default': qrbug.DEFAULT_DB_PATH,
    'journal-incident': qrbug.INCIDENTS_FILE_PATH,
}

async def run(incidents: List[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]
    FILE_CHUNK_SIZE_BYTES = 100_000

    async def stream_html_from_path(path: Path, stream):
        with open(path, 'r', encoding='utf-8') as f:
            while True:
                text = f.read(FILE_CHUNK_SIZE_BYTES)
                if not text:
                    break
                await stream.write(
                    html.escape(text)
                )
                await asyncio.sleep(0)

    await request.write(
        '<style>pre { font-family: monospace, monospace; background: #FFC; }</style>\n\n'
    )
    await request.write(f'<h2>{qrbug.Failure.instances[incident.failure_id].value} :</h2><pre>')
    await stream_html_from_path(FILENAME[incident.failure_id], request)
    await request.write('</pre>\n')

    return None
