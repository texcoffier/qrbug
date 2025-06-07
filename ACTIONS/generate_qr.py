from typing import Optional
from aiohttp import web
import base64
from io import BytesIO
import qrcode

import qrbug

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing

async def run(incidents: list[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    IMAGE_FORMAT = 'PNG'
    REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

    requested_thing_id = incident.comment
    url = REPORT_THING_URL.format(requested_thing_id)

    img = qrcode.make(url)

    buffer = BytesIO()
    img.save(buffer, format=IMAGE_FORMAT)
    img_base64 = base64.b64encode(buffer.getvalue())

    # TODO : générer les QR codes de tous les objets fils de ceux passés en paramètre
    # sorted(Thing[id] for id in get_all_children_ids(), key=lambda x: x.path())

    # Writes the HTML of the QR code
    await request.response.write((
        f'<h2>QR Code pour {requested_thing_id}</h2>'
        f'<div><img src="data:image/{IMAGE_FORMAT.lower()};base64,{img_base64.decode()}" /></div>'
    ).encode('utf-8'))
