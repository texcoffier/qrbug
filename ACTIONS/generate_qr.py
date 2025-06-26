from typing import Optional
import base64
from io import BytesIO
import qrcode
import qrbug

IMAGE_FORMAT = 'PNG'

QR_GEN_STATIC_FILES_PATH = qrbug.STATIC_FILES_PATH
TEMPLATE_CSS_PATH = QR_GEN_STATIC_FILES_PATH / 'qr_stylesheet.css'
TEMPLATE_QR_DISPLAY_CONFIG_BLOCK = QR_GEN_STATIC_FILES_PATH / 'qr_display_config.html'

# Run by a dispatcher:
#    thing: building, room, pc...
#    failure: print qr code
#    incidents: descendants of the thing

async def get_qr_code_b64_image(url: str) -> bytes:
    img = qrcode.make(url, border=0)
    buffer = BytesIO()
    img.save(buffer, format=IMAGE_FORMAT)
    img_base64 = base64.b64encode(buffer.getvalue())
    return img_base64

def get_css_template(force_load: bool = False) -> str:
    template_css_last_modified = TEMPLATE_CSS_PATH.stat().st_mtime
    if force_load or get_css_template._template_last_modified_timestamp != template_css_last_modified:
        template = TEMPLATE_CSS_PATH.read_text()
        get_css_template._template_last_modified_timestamp = template_css_last_modified
        get_css_template._template_cached_string = template
    else:
        template = get_css_template._template_cached_string
    return template

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

    TEMPLATE_CSS = (f'<style>\n{get_css_template()}\n</style>\n'
                    .replace('%cols%', default_cols)
                    .replace('%rows%', default_rows)
                    )

    TEMPLATE_QR_BLOCK = '<a href="{url}" target="_blank" class="qr_inner_block qr_{depth_class}"><div class="qr_report_me">{line_1}<br>{line_2}</div><div class="qr_thing_id">{thing_id}</div><img src="data:image/{img_format};base64,{img_b64}"></a>'
    await request.write(TEMPLATE_CSS)
    await request.write(TEMPLATE_QR_DISPLAY_CONFIG_BLOCK.read_text()
        .replace(f'<option>{default_cols}</option>', f'<option selected>{default_cols}</option>')
        .replace(f'<option>{default_rows}.</option>', f'<option selected>{default_rows}.</option>')
        )

    for requested_thing in requested_things:
        for thing_id, depth in requested_thing.get_sorted_children_ids():
            url = f'{qrbug.SERVICE_URL}/thing={thing_id}'
            if depth == 0:
                depth_class = 'root'
            elif depth == 1:
                depth_class = 'child'
            else:
                depth_class = 'descendant'
            # Writes the HTML of the QR code
            await request.write(TEMPLATE_QR_BLOCK.format(
                qr_link     =  f'/?thing-id={thing_id}&failure-id={incident.failure_id}&secret={request.secret.secret}',
                thing_id    = thing_id,
                url         = url,
                img_format  = IMAGE_FORMAT.lower(),
                img_b64     = (await get_qr_code_b64_image(url)).decode(),
                depth_class = depth_class,
                line_1      = qrbug.message('qrcode_line_1'),
                line_2      = qrbug.message('qrcode_line_2'),
            ))
    return None


get_css_template(force_load=True)
