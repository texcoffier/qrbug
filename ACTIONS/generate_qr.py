from typing import Optional
import base64
from io import BytesIO
import qrcode

import qrbug


IMAGE_FORMAT = 'PNG'
REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

QR_GEN_THING_ID = 'QR_GEN'
QR_GEN_FAILURE_ID = 'generate_qr'


def get_qr_gen_link(thing_id: qrbug.ThingId, ticket: str) -> str:
    return f'/?thing-id={QR_GEN_THING_ID}&failure-id={QR_GEN_FAILURE_ID}&what=thing&is-repaired=0&&additional-info={thing_id}&ticket={ticket}'

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing

async def run(incidents: list[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]

    requested_thing_id = incident.active[0].comment
    requested_thing = qrbug.Thing[requested_thing_id]

    if not requested_thing:
        return qrbug.action_helpers.ActionReturnValue(error_msg=f"Thing {repr(requested_thing_id)} not found")

    for thing_id in [requested_thing_id, *requested_thing.get_all_children_ids()]:
        url = REPORT_THING_URL.format(thing_id)

        img = qrcode.make(url)

        buffer = BytesIO()
        img.save(buffer, format=IMAGE_FORMAT)
        img_base64 = base64.b64encode(buffer.getvalue())

        # TODO : générer les QR codes de tous les objets fils de ceux passés en paramètre
        # sorted(Thing[id] for id in get_all_children_ids(), key=lambda x: x.path())

        # Writes the HTML of the QR code
        await request.response.write((
            f'<div class="qr_block">'
            f'<h2>QR Code pour <a href="{get_qr_gen_link(thing_id, request.query.get("ticket", ""))}">{thing_id}</a></h2>'
            f'<div><img src="data:image/{IMAGE_FORMAT.lower()};base64,{img_base64.decode()}" /></div>'
            f'</div>'
        ).encode('utf-8'))

    await request.response.write((
        b'<h3>Parents :</h3>'
        b'<ul>'
    ))
    for parent_id in requested_thing.parent_ids:
        await request.response.write(
            f'<li><a href="{get_qr_gen_link(parent_id, request.query.get("ticket", ""))}">{parent_id}</a></li>'.encode('utf-8')
        )
    await request.response.write(b'</ul>')

    return None
