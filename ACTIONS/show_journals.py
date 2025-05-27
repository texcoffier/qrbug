from typing import Optional
from aiohttp import web

import qrbug


async def run(incident: qrbug.Incidents, _request: web.Request) -> Optional[str]:
    from pathlib import Path
    import qrbug


    def get_html_from_path(path: Path):
        return path.read_text(encoding='utf-8').replace('\n', '<br/>\n')

    if incident.failure_id == 'SHOW_JOURNALS':
        db_file_contents = get_html_from_path(qrbug.DB_FILE_PATH)
        default_db_file_contents = get_html_from_path(qrbug.DEFAULT_DB_PATH)
        incidents_file_contents = get_html_from_path(qrbug.INCIDENTS_FILE_PATH)
        return (f'<h2>Default DB :</h2><div class="code">{default_db_file_contents}</div>\n'
                f'<h2>DB :</h2><div class="code">{db_file_contents}</div>\n'
                f'<h2>Incidents:</h2><div class="code">{incidents_file_contents}</div>')
    return None