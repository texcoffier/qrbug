import asyncio
import email.header
import email.utils
from typing import Union, Optional
import smtplib
import qrbug

def open_smtp_session(server):
    if ':' in server:
        server, port = server.rsplit(':', 1)
    else:
        port = 0
    send_mail.session = smtplib.SMTP(server, port, timeout=15)

async def send_mail_smtp(sender: str, recipients: Union[tuple[str, ...], list[str]], body: bytes):
    smtp_result = 'NotSent'
    for server in qrbug.SMTP_SERVER: # Try each SMTP server if failure
        try:
            try:
                smtp_result = send_mail.session.sendmail(sender, recipients, body)
                # Mail sent
                break
            except (AttributeError, # because 'session' is None the first time
                    smtplib.SMTPServerDisconnected,
                    smtplib.SMTPSenderRefused):
                open_smtp_session(server)
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
    to      : str,
    subject : str,
    message : str,
    sender  : Optional[str] = None,
    show_to : bool          = False,
    reply_to: Optional[str] = None,
    error_to: Optional[str] = None,
    cc      : tuple[str]    = ()
    ):

    def encode(x):
        return email.header.Header(x.strip()).encode()

    def cleanup(x):
        return [encode(addr)
                for addr in x or ()
                if addr and '@' in addr and '.' in addr
                ]

    if isinstance(to, str):
        to = [to]
    if sender is None:
        sender = qrbug.SMTP_DEFAULT_SENDER

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

    # Logs the mail to the logs folder
    qrbug.log_email(body)

    return await send_mail_smtp(sender, recipients, body)  # TODO: Spawn un subprocess

send_mail.session = None


def get_user_from_login(login: str) -> str:
    return qrbug.DEFAULT_EMAIL_TO  # TODO: Remplacer ça


qrbug.send_mail = send_mail
qrbug.get_user_from_login = get_user_from_login
