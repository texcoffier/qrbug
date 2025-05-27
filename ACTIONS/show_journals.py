from typing import Optional
from aiohttp import web

import qrbug


# TODO: Make this less XSS friendly
# TODO: Stream the answer

# TODO: Clore l'incident qui a été créé pour ce DEBUG -> Rajouter un attribut 'auto-close' à failure, qui met que la failure est réparée tout de suite
# TODO:                                               -> **OU** faire en sorte que le dispatcher répare la failure, avec le 'auto-close' spécifié dans le dispatcher
async def run(incident: qrbug.Incidents, request: web.Request) -> Optional[str]:
    from pathlib import Path
    import qrbug


    async def get_html_from_path(path: Path):
        return path.read_text(encoding='utf-8')  # TODO: Lire 100Ko par 100Ko le fichier puis asyncio.sleep(0)

    if incident.failure_id.startswith('SHOW_JOURNALS'):
        failure_id = incident.failure_id.removeprefix('SHOW_JOURNALS')
        failure_id = failure_id.removeprefix('_')  # The majority of 'SHOW_JOURNALS' failures take the shape of 'SHOW_JOURNALS_*', so removing the underscore is necessary

        await request.response.write(
            '<style>pre { font-family: monospace, monospace; background: #FFC; }</style>\n\n'.encode('utf-8')
        )

        async def write(name: str, string: str):
            await request.response.write(f'<h2>{name} :</h2><pre>{string}</pre>\n'.encode('utf-8'))

        if failure_id in ('', 'ALL', 'DB'):
            await write('DB', await get_html_from_path(qrbug.DB_FILE_PATH))
        if failure_id in ('', 'ALL', 'DEFAULT_DB'):
            await write('Default DB', await get_html_from_path(qrbug.DEFAULT_DB_PATH))
        if failure_id in ('', 'ALL', 'INCIDENTS'):
            await write('Incidents', await get_html_from_path(qrbug.INCIDENTS_FILE_PATH))
    return None
