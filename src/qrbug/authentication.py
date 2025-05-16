import re
import time
import urllib.parse
from typing import Optional

import aiohttp
from aiohttp import web

# Token: Login, Timestamp, IP
LOGGED_USERS: dict[str, tuple[str, int, str]] = {}  # TODO: Classe Session ?
TOKEN_LOGIN_TIMEOUT = 60
CAS_URL = 'https://cas.univ-lyon1.fr/cas'
SERVICE_URL = 'http://qrbug.univ-lyon1.fr:8080/'


def get_login_from_token(token: str, user_ip: str) -> str:
    """
    Gets whether a user is logged in or not.
    Returns an empty string if the user is not logged in.
    Returns the login of the user if it is logged in.
    Requires a CAS token.
    """
    if token in LOGGED_USERS:
        login, timestamp, ip = LOGGED_USERS[token]
        if time.time() - timestamp < TOKEN_LOGIN_TIMEOUT and ip == user_ip:
            return login
    return ''


def safe(txt: str) -> str:
    return re.sub("[^-_.a-zA-Z0-9/:,]", "_", txt)


async def validate_ticket(cas_url: str, service_url: str, ticket: str, user_ip: str) -> Optional[str]:
    """
    Validates that the given ticket for the given service URL is valid, and returns the user's login
    :returns: None if the login ticket is invalid, a string containing the user's login if it is valid
    """
    safe_ticket = safe(ticket)
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{cas_url}/validate?service={urllib.parse.quote(service_url)}&ticket={safe_ticket}') as response:
            assert response.status == 200, f'Something went wrong when validating login ticket, code {response.status}'
            response_text = await response.text()
            final_response = response_text.split('\n')  # Response is either 'no\n\n' or 'yes\n' and the login
            if final_response[0].strip() == 'yes':
                user_login = final_response[1].strip()
                LOGGED_USERS[safe_ticket] = (user_login, int(time.time()), user_ip)
                return user_login
            else:
                return None


async def handle_login(request: web.Request, extra_url: str = '') -> Optional[str]:
    service_url = SERVICE_URL + ('/' if not SERVICE_URL.endswith('/') else '') + extra_url
    login_ticket: Optional[str] = request.query.get("ticket", None)
    if login_ticket is None:
        raise web.HTTPTemporaryRedirect(f'{CAS_URL}/login?service={service_url}')
    else:
        user_login = get_login_from_token(login_ticket, request.remote)
        if not user_login:
            user_login = await validate_ticket(CAS_URL, service_url, login_ticket, request.remote)
    return user_login
