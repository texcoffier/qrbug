from typing import Optional
from aiohttp import web

import qrbug

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing

async def run(incidents: List[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    import base64
    from io import BytesIO
    import qrbug
    import qrcode

    incident = incidents[0]

    REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

    requested_thing_id = incident.comment
    url = REPORT_THING_URL.format(requested_thing_id)

    img = qrcode.make(url)

    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_base64 = base64.b64encode(buffer.getvalue())

    # Writes the HTML of the QR code
    await request.response.write((
        f'<h2>QR Code pour {requested_thing_id}</h2>'
        f'<div><img src="data:image/jpeg;base64,{img_base64.decode()}" /></div>'
    ).encode('utf-8'))

    incident.incident_del()