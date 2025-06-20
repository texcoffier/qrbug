from typing import Optional
import base64
from io import BytesIO

import qrcode

import qrbug


IMAGE_FORMAT = 'PNG'
IS_WYSIWYG = True
REPORT_THING_URL = qrbug.SERVICE_URL + '/thing={}'

QR_GEN_STATIC_FILES_PATH = qrbug.STATIC_FILES_PATH
TEMPLATE_CSS_PATH = QR_GEN_STATIC_FILES_PATH / 'qr_stylesheet.css'
TEMPLATE_JS_PATH = QR_GEN_STATIC_FILES_PATH / 'qr_script.js'
TEMPLATE_QR_BLOCK_PATH = QR_GEN_STATIC_FILES_PATH / 'qr_inner_block.html'
TEMPLATE_QR_CONFIG_BLOCK = QR_GEN_STATIC_FILES_PATH / 'qr_config.html'
TEMPLATE_QR_DISPLAY_CONFIG_BLOCK = QR_GEN_STATIC_FILES_PATH / 'qr_display_config.html'
TEMPLATE_QR_INFOS_BLOCK = QR_GEN_STATIC_FILES_PATH / 'qr_infos_block.html'
TEMPLATE_QR_PARENT_LINKS = QR_GEN_STATIC_FILES_PATH / 'qr_parent_links.html'


def get_qr_gen_link(thing_id: qrbug.ThingId, failure_id, secret: str) -> str:
    return f'/?thing-id={thing_id}&failure-id={failure_id}&secret={secret}'

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing


async def get_qr_code_b64_image(url: str) -> bytes:
    img = qrcode.make(url)
    buffer = BytesIO()
    img.save(buffer, format=IMAGE_FORMAT)
    img_base64 = base64.b64encode(buffer.getvalue())
    return img_base64


async def run(incidents: list[qrbug.Incident], request: qrbug.Request) -> Optional[qrbug.action_helpers.ActionReturnValue]:
    incident = incidents[0]
    row_cols_number = incident.failure_id.split('_')[-1]
    if row_cols_number != '':
        default_rows, default_cols = row_cols_number.split('x')
    else:
        default_rows = '4'
        default_cols = '4'

    requested_things = [incident.thing]
    additional_things = incident.active[0].comment.split(',')
    if incident.active[0].comment:
        requested_things.extend(qrbug.Thing[thing_id] for thing_id in additional_things)

    for i, requested_thing in enumerate(requested_things):
        if not requested_thing:
            if i == 0:
                requested_thing_id = incident.thing_id
            else:
                requested_thing_id = additional_things[i - 1]
            return qrbug.action_helpers.ActionReturnValue(error_msg=f"Thing {repr(requested_thing_id)} not found")

    TEMPLATE_CSS = (f'<style>\n{TEMPLATE_CSS_PATH.read_text()}\n</style>\n'
                    .replace('%cols%', default_cols)
                    .replace('%rows%', default_rows)
                    .replace('%qr_info_title_display%', 'none' if IS_WYSIWYG else 'block')
                    .replace('%qr_side_text_display%',  'block' if IS_WYSIWYG else 'none')
                    .replace('%qr_img_max_width%',      'var(--qr-width)' if IS_WYSIWYG else 'auto')
                    )
    TEMPLATE_JS = f'<script>\n{TEMPLATE_JS_PATH.read_text()}\n</script>\n'
    TEMPLATE_QR_BLOCK = TEMPLATE_QR_BLOCK_PATH.read_text()
    await request.write(TEMPLATE_CSS)
    await request.write(TEMPLATE_JS)
    await request.write(TEMPLATE_QR_DISPLAY_CONFIG_BLOCK.read_text())
    # await request.write_newline(TEMPLATE_QR_INFOS_BLOCK.read_text())
    # await request.write_newline(
    #     '<div class="qr_parent_links">',
    #     '   <h3>Parents :</h3>',
    #     '   <ul>',
    # )
    # for parent_id in requested_thing.parent_ids:
    #     await request.write_newline(
    #         f'      <li><a href="{get_qr_gen_link(parent_id, incident.failure_id, user_ticket)}">{parent_id}</a></li>'
    #     )
    # await request.write_newline(
    #     '   </ul>',
    #     '</div>'
    # )
    #await request.write_newline(TEMPLATE_QR_CONFIG_BLOCK.read_text())
    await request.write_newline('<div class="qr_outer_block">')

    for requested_thing in requested_things:
        for thing_id, depth in requested_thing.get_sorted_children_ids():
            url = REPORT_THING_URL.format(thing_id)
            img_base64 = await get_qr_code_b64_image(url)

            if depth == 0:
                depth_class = 'root'
            elif depth == 1:
                depth_class = 'child'
            else:
                depth_class = 'descendant'

            # Writes the HTML of the QR code
            await request.write(TEMPLATE_QR_BLOCK.format(
                qr_link     = get_qr_gen_link(thing_id, incident.failure_id, request.secret.secret),
                thing_id    = thing_id,
                url         = url,
                img_format  = IMAGE_FORMAT.lower(),
                img_b64     = img_base64.decode(),
                depth_class = depth_class
            ))

    await request.write('</div>\n')

    return None
