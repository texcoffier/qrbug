from typing import Optional
from aiohttp import web
import base64
from io import BytesIO
import qrcode

import qrbug


IMAGE_FORMAT = 'PNG'
REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing

async def run(incidents: list[qrbug.Incident], request: web.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    if incident.failure_id == 'qrcode':
        requested_thing_id = incident.comment
        img_base64 = await get_qrcode_b64(requested_thing_id)

    # TODO : générer les QR codes de tous les objets fils de ceux passés en paramètre
    # sorted(Thing[id] for id in get_all_children_ids(), key=lambda x: x.path())

        # Writes the HTML of the QR code
        await request.response.write((
            f'<h2>QR Code pour {requested_thing_id}</h2>'
            f'<div><img src="data:image/{IMAGE_FORMAT.lower()};base64,{img_base64.decode()}" /></div>'
        ).encode('utf-8'))
    else:
        format = incident.failure_id.lstrip('qrcode-')
        page_type, rows, cols = format.split('-')

        thing_ids = ['test1', 'test2']  # TODO: Replace with the actual thing IDs of this Thing's children

        await request.response.write(f'<div style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr); grid-template-rows: repeat({rows}, minmax(0, 1fr); gap: 0px;"></div>'.encode('utf-8'))

        for thing_id in thing_ids:
            await request.response.write((
                f'<div><div><img src="data:image/{IMAGE_FORMAT.lower()};base64,{(await get_qrcode_b64(thing_id)).decode('utf-8')}" /></div>'
                f'<h4>{thing_id}</h4></div>'
            ).encode('utf-8'))

        await request.response.write(b'</div>')

    incident.incident_del()


async def get_qrcode_b64(requested_thing_id: qrbug.ThingId):
    url = REPORT_THING_URL.format(requested_thing_id)
    img = qrcode.make(url)
    buffer = BytesIO()
    img.save(buffer, format=IMAGE_FORMAT)
    img_base64 = base64.b64encode(buffer.getvalue())
    return img_base64