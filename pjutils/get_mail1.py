#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, imaplib, rfc822
import string, re, StringIO
import email
from email.charset import Charset
import quopri
import pprint

M = imaplib.IMAP4('dev.parasykjiems.lt', 5143)
M.login_cram_md5('vytautas', 'devdev')
code, mailboxen = M.list()
M.select('INBOX')
messages = []
chrst = Charset()
#insert_response = InsertResponse()
typ, data = M.search(None, 'To', 'reply116_1223456')

#typ, data = M.search(None, 'UNSEEN')

messages_list = []

for num in data[0].split():
    typ, msg_data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (To)])')
    to = msg_data[0][1].split('@')[0].replace('To: ','')
    if 'reply' in to:
        receiver = to.split('_')
        msg_id = receiver[0].replace('reply','')
        msg_hash = receiver[1]

        typ, msg_data = M.fetch(num, '(RFC822)')
        for response_part in msg_data:

            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                print msg.get_charset()
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            msg_text = part.get_payload().decode('quoted-printable')
                else:
                    msg_text = msg.get_payload().decode('quoted-printable')
        message_data = {'msg_id':msg_id, 'msg_hash':msg_hash, 'msg_text':msg_text}
        messages_list.append(message_data)

    else:
        M.store(num, '+FLAGS', '\\Deleted')

print messages_list
M.expunge()
M.close()
M.logout()
#return messages

