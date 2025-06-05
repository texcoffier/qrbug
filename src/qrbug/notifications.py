import asyncio
import email.header
import email.utils
import html
import os
import re
import time
from typing import Union, Optional

import qrbug


async def send_mail_smtp(sender: str, recipients: Union[tuple[str, ...], list[str]], body: bytes):
    import smtplib

    smtp_result = 'NotSent'
    for server in re.split(' +', os.getenv('QRBUG_SMTP_SERVER')) * 2:
        if ':' in server:
            server, port = server.rsplit(':', 1)
        else:
            port = 0

        try:
            try:
                smtp_result = send_mail.session.sendmail(sender, recipients, body)
                # Mail sent
                break
            except (AttributeError, # because 'session' is None the first time
                    smtplib.SMTPServerDisconnected,
                    smtplib.SMTPSenderRefused):
                send_mail.session = smtplib.SMTP(server, port, timeout=15)
                smtp_result = send_mail.session.sendmail(sender, recipients, body)
                break # Mail sent
        except smtplib.SMTPRecipientsRefused:
            # Next server
            pass
        await asyncio.sleep(0)

    if smtp_result == 'NotSent':
        if isinstance(recipients, str):
            smtp_result = {'': recipients}
        else:
            smtp_result = {k: '???' for k in recipients}

    if smtp_result:
        error_string = ""
        for recipient, error in smtp_result.items():
            error_string += f'{recipient}: {error}\n'
        return error_string
    return None


async def send_mail(
        to: str, subject: str, message: str, sender: Optional[str] = None,
        show_to: bool = False, reply_to: Optional[str] = None,
        error_to: Optional[str] = None, cc: tuple[str] = tuple()
):

    def encode(x):
        return email.header.Header(x.strip()).encode()

    def decode(x):  # pragma: no cover
        txt, enc = email.header.decode_header(x)[0]
        return txt.decode(enc)

    def cleanup(x):
        return [encode(addr)
                for addr in x or ()
                if addr and '@' in addr and '.' in addr
                ]

    if isinstance(to, str):
        to = [to]
    if sender is None:
        sender = os.getenv('QRBUG_SMTP_DEFAULT_SENDER')

    to = cleanup(to)
    cc = cleanup(cc)
    if len(to) == 0 and len(cc) == 0:
        return None
    if len(to) == 1:
        show_to = True
    header = ["From: {}\n".format(encode(reply_to or sender))]

    s = subject.replace('\n', ' ').replace('\r', ' ')[:300]
    header.append("Subject: " + encode(s) + '\n')
    if show_to:
        for tto in to:
            header.append("To: {}\n".format(tto))
    for tto in cc:
        header.append("CC: {}\n".format(tto))
    if reply_to:
        header.append('Return-Path: {}\n'.format(encode(sender)))
    if error_to:
        header.append('Error-To: {}\n'.format(encode(error_to)))

    if message.startswith('<html>') or message.startswith('<!DOCTYPE html>'):
        header.append('Content-Type: text/html; charset="utf-8"\n')
    else:
        header.append('Content-Type: text/plain; charset="utf-8"\n')

    header.append("Date: " + email.utils.formatdate(localtime=True) + '\n')
    header.append("Content-Transfer-Encoding: 8bit\n")
    header.append("MIME-Version: 1.0\n")
    header.append('\n')
    header = ''.join(header).replace("\n", "\r\n")
    recipients = tuple(to) + tuple(cc)
    body = (header + message).encode('utf-8')
    return await send_mail_smtp(sender, recipients, body)

send_mail.session = None


def get_email_contents(incident: qrbug.Incident) -> str:
    email_body = [
        f'QRBUG: Un incident s\'est produit sur la machine {repr(incident.thing_id)} avec la panne {repr(incident.failure_id)}.'
    ]
    if len(incident.active) > 0:
        email_body.append('\n\n')
        email_body.append(f'Cet incident a été signalé un total de {len(incident.active)} fois par :\n')
        for report in incident.active:
            email_body.append(f'- {report.login} (IP: {report.ip}) le {time.strftime("%d/%m/%Y à %H:%M:%S")}\n')
            if report.comment:
                email_body.append(f'  - Avec le commentaire: {html.escape(report.comment)}\n')
    return ''.join(email_body)


qrbug.send_mail = send_mail
qrbug.get_email_contents = get_email_contents
