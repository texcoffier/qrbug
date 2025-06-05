import email.header
import email.utils
import os
import re
from typing import Union


def send_mail_smtp(sender: str, recipients: Union[tuple[str, ...], list[str]], body: bytes):
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


def send_mail(to, subject, message, sender=None, show_to=False, reply_to=None,
              error_to=None, cc=()):

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
    header = "From: {}\n".format(encode(reply_to or sender))

    s = subject.replace('\n', ' ').replace('\r', ' ')[:300]
    header += "Subject: " + encode(s) + '\n'
    if show_to:
        for tto in to:
            header += "To: {}\n".format(tto)
    for tto in cc:
        header += "CC: {}\n".format(tto)
    if reply_to:
        header += 'Return-Path: {}\n'.format(encode(sender))
    if error_to:
        header += 'Error-To: {}\n'.format(encode(error_to))  # pragma: no cover

    if message.startswith('<html>') or message.startswith('<!DOCTYPE html>'):
        header += 'Content-Type: text/html; charset="utf-8"\n'
    else:
        header += 'Content-Type: text/plain; charset="utf-8"\n'

    header += "Date: " + email.utils.formatdate(localtime=True) + '\n'
    header += "Content-Transfer-Encoding: 8bit\n"
    header += "MIME-Version: 1.0\n"
    header += '\n'
    header = header.replace("\n", "\r\n")
    recipients = tuple(to) + tuple(cc)
    body = (header + message).encode('utf-8')
    return send_mail_smtp(sender, recipients, body)

send_mail.session = None
