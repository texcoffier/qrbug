from typing import Optional
import base64
from io import BytesIO

import qrcode

import qrbug


IMAGE_FORMAT = 'PNG'
REPORT_THING_URL = qrbug.SERVICE_URL + ('/' if not qrbug.SERVICE_URL.endswith('/') else '') + 'thing={}'

QR_GEN_STATIC_FILES_PATH = qrbug.STATIC_FILES_PATH / 'QR_GENERATION'
TEMPLATE_CSS_PATH = QR_GEN_STATIC_FILES_PATH / 'generate_qr.css'
TEMPLATE_QR_BLOCK_PATH = QR_GEN_STATIC_FILES_PATH / 'qr_inner_block.html'
TEMPLATE_QR_CONFIG_BLOCK = QR_GEN_STATIC_FILES_PATH / 'qr_config.html'
TEMPLATE_QR_INFOS_BLOCK = QR_GEN_STATIC_FILES_PATH / 'qr_infos_block.html'
TEMPLATE_QR_PARENT_LINKS = QR_GEN_STATIC_FILES_PATH / 'qr_parent_links.html'


def get_qr_gen_link(thing_id: qrbug.ThingId, failure_id, ticket: str) -> str:
    return f'/?thing-id={thing_id}&failure-id={failure_id}&ticket={ticket}'

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing

async def run(incidents: list[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]
    row_cols_number = incident.failure_id.split('_')[-1]
    if row_cols_number != '':
        default_rows, default_cols = row_cols_number.split('x')
    else:
        default_rows = '4'
        default_cols = '4'

    requested_thing = incident.thing

    if not requested_thing:
        return qrbug.action_helpers.ActionReturnValue(error_msg=f"Thing {repr(requested_thing.id)} not found")

    user_ticket = request.query.get("ticket", "")
    TEMPLATE_CSS = (f'<style>\n{TEMPLATE_CSS_PATH.read_text()}\n</style>'
                    .replace('%cols%', default_cols)
                    .replace('%rows%', default_rows))
    TEMPLATE_QR_BLOCK = TEMPLATE_QR_BLOCK_PATH.read_text()
    await request.write(TEMPLATE_CSS)
    await request.write_newline(TEMPLATE_QR_INFOS_BLOCK.read_text())
    await request.write_newline(
        '<div class="qr_parent_links">',
        '   <h3>Parents :</h3>',
        '   <ul>',
    )
    for parent_id in requested_thing.parent_ids:
        await request.write_newline(
            f'      <li><a href="{get_qr_gen_link(parent_id, incident.failure_id, user_ticket)}">{parent_id}</a></li>'
        )
    await request.write_newline(
        '   </ul>',
        '</div>'
    )
    #await request.write_newline(TEMPLATE_QR_CONFIG_BLOCK.read_text())
    await request.write_newline('<div class="qr_outer_block">')

    for thing_id in [requested_thing.id, *requested_thing.get_all_children_ids()]:
        url = REPORT_THING_URL.format(thing_id)

        img = qrcode.make(url)

        buffer = BytesIO()
        img.save(buffer, format=IMAGE_FORMAT)
        img_base64 = base64.b64encode(buffer.getvalue())

        # TODO : générer les QR codes de tous les objets fils de ceux passés en paramètre
        # sorted(Thing[id] for id in get_all_children_ids(), key=lambda x: x.path())

        # Writes the HTML of the QR code
        await request.write(TEMPLATE_QR_BLOCK.format(
            qr_link    = get_qr_gen_link(thing_id, incident.failure_id, user_ticket),
            thing_id   = thing_id,
            url        = url,
            img_format = IMAGE_FORMAT.lower(),
            img_b64    = img_base64.decode(),
        ))

    await request.write('</div>')

    return None
