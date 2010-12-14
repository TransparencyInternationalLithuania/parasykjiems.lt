#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, imaplib, rfc822
import string, re, StringIO
import email
from email.charset import Charset
import quopri

class GetMail():

    def get_imap(self, server_info, msg_id, response_hash):
# use IMAP4_SSL when SSL is supported on mail server
#        M = imaplib.IMAP4_SSL(server_info['server'])
# use login, when plaintext login is supported
#        M.login(server_info['username'], server_info['password'])
# use IMAP4 when SSL is not supported on mail server
        M = imaplib.IMAP4(server_info['server'], server_info['port'])
# use login_cram_md5(or some other supported login type) plaintext login is not supported
        M.login_cram_md5(server_info['username'], server_info['password'])
        M.select()
        messages = []
        chrst = Charset()
#        typ, data = M.search(None, 'To', 'reply%s_%s' % (msg_id, response_hash))
        typ, data = M.search(None, 'To', 'reply%s_%s' % (msg_id, response_hash))
        for num in data[0].split():
            message = ""
#            typ, data = M.fetch(num, '(RFC822)')

            typ, data = M.fetch(num, '(BODY[1])')

            file = StringIO.StringIO(data[0][1])

            message = rfc822.Message(file)

            mssg = message.fp.read()
            mssg = quopri.decodestring(mssg)#mssg.decode('quoted-printable')
#            encoded = mssg.encode('iso-8859-13')
#            decoded = unicode(encoded, 'utf-8')
#            print decoded
            messages.append(mssg)

        M.close()
        M.logout()
        return messages

    def get_pop3(self, server_info, msg_id):
        print 'Not yet implemented'
        return []

    def get_mail(self, server_info, msg_id, response_hash):
        messages = []
        if server_info['type'] == 'IMAP':
            messages = self.get_imap(server_info, msg_id, response_hash)
        elif server_info['type'] == 'POP3':
            messages = self.get_pop3(server_info, msg_id, response_hash)
        return messages

