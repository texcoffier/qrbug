from typing import Optional
import base64
from io import BytesIO
from pathlib import Path

import qrcode

import qrbug


IMAGE_FORMAT = 'PNG'
REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

QR_GEN_THING_ID = 'QR_GEN'
QR_GEN_FAILURE_ID = 'generate_qr'

TEMPLATE_CSS_PATH = Path('STATIC') / 'generate_qr.css'
TEMPLATE_QR_BLOCK_PATH = Path('STATIC') / 'qr_inner_block.html'


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

    user_ticket = request.query.get("ticket", "")
    TEMPLATE_CSS = f'<style>\n{TEMPLATE_CSS_PATH.read_text()}\n</style>'
    TEMPLATE_QR_BLOCK = TEMPLATE_QR_BLOCK_PATH.read_text()
    await request.write(TEMPLATE_CSS)
    await request.write('<div class="qr_outer_block">')

    for thing_id in [requested_thing_id, *requested_thing.get_all_children_ids()]:
        url = REPORT_THING_URL.format(thing_id)

        img = qrcode.make(url)

        buffer = BytesIO()
        img.save(buffer, format=IMAGE_FORMAT)
        img_base64 = base64.b64encode(buffer.getvalue())

        # TODO : générer les QR codes de tous les objets fils de ceux passés en paramètre
        # sorted(Thing[id] for id in get_all_children_ids(), key=lambda x: x.path())

        # Writes the HTML of the QR code
        await request.write(TEMPLATE_QR_BLOCK.format(
            qr_link    = get_qr_gen_link(thing_id, user_ticket),
            thing_id   = thing_id,
            img_format = IMAGE_FORMAT.lower(),
            img_b64    = img_base64.decode(),
        ))

    await request.write('</div>')
    await request.write(
        '<div class="qr_parent_links">'
        '   <h3>Parents :</h3>'
        '   <ul>'
    )
    for parent_id in requested_thing.parent_ids:
        await request.write(
            f'      <li><a href="{get_qr_gen_link(parent_id, user_ticket)}">{parent_id}</a></li>'
        )
    await request.write('   </ul>\n</div>')

    return None
