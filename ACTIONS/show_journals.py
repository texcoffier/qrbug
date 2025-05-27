from typing import Optional
from aiohttp import web

import qrbug


async def run(incident: qrbug.Incidents, _request: web.Request) -> Optional[str]:
    from pathlib import Path
    import qrbug


    def get_html_from_path(path: Path):
        return path.read_text(encoding='utf-8')

    if incident.failure_id == 'SHOW_JOURNALS':
        db_file_contents = get_html_from_path(qrbug.DB_FILE_PATH)
        default_db_file_contents = get_html_from_path(qrbug.DEFAULT_DB_PATH)
        incidents_file_contents = get_html_from_path(qrbug.INCIDENTS_FILE_PATH)
        return ( '<style>pre { font-family: monospace, monospace; background: #FFC; }</style>\n\n'
                f'<h2>Default DB :</h2><pre>{default_db_file_contents}</pre>\n'
                f'<h2>DB :</h2><pre>{db_file_contents}</pre>\n'
                f'<h2>Incidents:</h2><pre>{incidents_file_contents}</pre>')
    return None