from typing import Optional
from aiohttp import web

import qrbug


async def run(incident: qrbug.Incidents, request: web.Request) -> Optional[str]:
    from pathlib import Path
    import asyncio
    import qrbug

    FILE_CHUNK_SIZE_BYTES = 100_000


    async def stream_html_from_path(path: Path, stream):
        with open(path, 'r', encoding='utf-8') as f:
            while True:
                text = f.read(FILE_CHUNK_SIZE_BYTES)
                if not text:
                    break
                await stream.write(
                    text.replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .encode('utf-8')
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
        'INCIDENTS': ('Incidents', qrbug.INCIDENTS_FILE_PATH)
    }

    async def write(name: str, journal_path: Path):
        await request.response.write(f'<h2>{name} :</h2><pre>'.encode('utf-8'))
        await stream_html_from_path(journal_path, request.response)
        await request.response.write('</pre>\n'.encode('utf-8'))

    for journal in failure_id.split('-'):
        current_journal = translation_table[journal]
        current_journal_name = current_journal[0]
        current_journal_path = current_journal[1]
        await write(current_journal_name, current_journal_path)

    return None
