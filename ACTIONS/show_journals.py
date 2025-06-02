from typing import Optional
from aiohttp import web

import qrbug


@qrbug.action_helpers.auto_close_incident
async def run(incident: qrbug.Incident, request: web.Request) -> Optional[str]:
    from pathlib import Path
    import asyncio
    import html
    import qrbug

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


    if not incident.failure_id.startswith('SHOW_JOURNALS'):
        return None

    failure_id = incident.failure_id.removeprefix('SHOW_JOURNALS').lstrip('_')

    await request.response.write(
        b'<style>pre { font-family: monospace, monospace; background: #FFC; }</style>\n\n'
    )

    translation_table = {  # Values : (name, path)
        'DB': ('Configuration', qrbug.DB_FILE_PATH),
        'DEFAULT_DB': ('Configuration par défaut', qrbug.DEFAULT_DB_PATH),
        'INCIDENTS': ('Incident', qrbug.INCIDENTS_FILE_PATH)
    }

    for journal in failure_id.split('-'):
        journal_name, journal_path = translation_table[journal]
        await request.response.write(f'<h2>{journal_name} :</h2><pre>'.encode('utf-8'))
        await stream_html_from_path(journal_path, request.response)
        await request.response.write('</pre>\n'.encode('utf-8'))

    return None
