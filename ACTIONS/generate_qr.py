import qrcode

BASE_URL = 'https://qrbug.univ-lyon1.fr'
REPORT_THING_URL = BASE_URL + '/thing={}'

def run(incident: Incidents):
    url = REPORT_THING_URL.format(incident.thing_id)
    img = qrcode.make(url)
    img.show()
