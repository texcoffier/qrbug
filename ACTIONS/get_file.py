"""
Display any STATIC HTML file on browser
The filename is the failure_id.
"""
import html
import qrbug

async def run(incidents, request):
    filename = incidents[0].failure_id
    if '/' in filename:
        await request.write(f'Access to «{html.escape(filename)} not authorized')
        return
    filename = qrbug.STATIC_FILES_PATH / filename
    if filename.exists() and filename.is_file():
        await request.write(filename.read_text(encoding='utf-8'))
    else:
        await request.write(f'«{html.escape(str(filename))} does not exists')
