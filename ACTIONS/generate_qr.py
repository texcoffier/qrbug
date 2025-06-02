from typing import Optional
from aiohttp import web

import qrbug


@qrbug.action_helpers.auto_close_incident
async def run(incident: qrbug.Incident, request: web.Request) -> Optional[str]:
    import base64
    from io import BytesIO
    import qrbug
    import qrcode

    REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

    requested_thing_id = incident.comment
    url = REPORT_THING_URL.format(requested_thing_id)

    img = qrcode.make(url)

    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_base64 = base64.b64encode(buffer.getvalue())

    # Writes the HTML of the QR code
    await request.response.write((
        f'<h2>QR Code for thing {requested_thing_id}</h2>'
        f'<div><img src="data:image/jpeg;base64,{img_base64.decode()}" /></div>'
    ).encode('utf-8'))
