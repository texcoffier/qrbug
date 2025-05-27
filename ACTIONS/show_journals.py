from typing import Optional
from aiohttp import web

import qrbug


async def run(incident: qrbug.Incidents, _request: web.Request) -> Optional[str]:
    from pathlib import Path
    import qrbug


    async def get_html_from_path(path: Path):
        return path.read_text(encoding='utf-8')

    if incident.failure_id.startswith('SHOW_JOURNALS'):
        failure_id = incident.failure_id.removeprefix('SHOW_JOURNALS')
        failure_id = failure_id.removeprefix('_')  # The majority of 'SHOW_JOURNALS' failures take the shape of 'SHOW_JOURNALS_*', so removing the underscore is necessary

        final_string: list[str] = ['<style>pre { font-family: monospace, monospace; background: #FFC; }</style>\n\n']

        def write(name: str, string: str):
            final_string.append(f'<h2>{name} :</h2><pre>{string}</pre>\n')

        if failure_id in ('', 'ALL', 'DB'):
            write('DB', await get_html_from_path(qrbug.DB_FILE_PATH))
        if failure_id in ('', 'ALL', 'DEFAULT_DB'):
            write('Default DB', await get_html_from_path(qrbug.DEFAULT_DB_PATH))
        if failure_id in ('', 'ALL', 'INCIDENTS'):
            write('Incidents', await get_html_from_path(qrbug.INCIDENTS_FILE_PATH))
        return ''.join(final_string)
    return None
