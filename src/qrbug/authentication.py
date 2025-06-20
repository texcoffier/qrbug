import re
import time
import random
import urllib.parse
from typing import Optional

import aiohttp
from aiohttp import web
import qrbug

def safe(txt: str) -> str:
    return re.sub("[^-_.a-zA-Z0-9/:,]", "_", txt)

def service_url(extra_url):
    return f'{qrbug.SERVICE_URL.rstrip("/")}/{extra_url.lstrip("/")}'

def redirect_url(extra_url):
    return f'{qrbug.CAS_URL}/login?service={urllib.parse.quote(service_url(extra_url))}'

def validate_url(extra_url):
    extra_url, ticket = extra_url.rsplit('ticket=', 1)
    extra_url = extra_url.rstrip('?&')
    return f'{qrbug.CAS_URL}/validate?service={urllib.parse.quote(service_url(extra_url))}&ticket={ticket}'

class Secret:
    instances: dict[str, "Secret"] = {}
    def __init__(self):
        self.secret = hex(random.randint(1, 0xFFFFFFFFFFFFFFFF))[2:]
        self.login = ''
        self.timestamp = time.time()
        self.instances[self.secret] = self

    def __str__(self):
        return f'Secret({self.secret}, {self.login}, {self.timestamp})'

    @classmethod
    def dump(self):
        print("Get")
        for i in Secret.instances.values():
            print(i)

    def is_valid(self) -> bool:
        """
        Limit the time life of a ticket
        """
        return time.time() - self.timestamp < qrbug.TOKEN_LOGIN_TIMEOUT

    @classmethod
    def get(cls, secret: str) -> Optional["Secret"]:
        """
        Return the secret if valid
        """
        session = Secret.instances.get(secret, None)
        if session:
            if session.is_valid():
                return session
            del cls.instances[secret]
        return None

    @classmethod
    def update_secret(cls, secret: str) -> str:
        """
        Create a secret if needed.
        """
        return cls.get(secret) or Secret()

    @classmethod
    async def get_login(cls, secret, query, extra_url):
        secret = Secret.instances[secret]
        if secret.login:
            return secret.login
        ticket = query.get('ticket', None)
        if not ticket:
            return None
        if extra_url.count('ticket=') > 1:
            return None
        if safe(ticket) != ticket:
            return None
        async with aiohttp.ClientSession() as session:
            async with session.get(validate_url(extra_url)) as response:
                assert response.status == 200, f'Something went wrong when validating login ticket, code {response.status}'
                response_text = await response.text()
                final_response = response_text.split('\n')  # Response is either 'no\n\n' or 'yes\n' and the login
                if final_response[0].strip() == 'yes':
                    secret.login = final_response[1].strip().lower()
                    return secret.login
                return None

qrbug.update_secret = Secret.update_secret
qrbug.check_secret = Secret.get
qrbug.get_login = Secret.get_login
qrbug.Secret = Secret

def redirect(extra_url: str = '') -> Optional[str]:
    raise web.HTTPTemporaryRedirect(redirect_url(extra_url))
qrbug.redirect = redirect
