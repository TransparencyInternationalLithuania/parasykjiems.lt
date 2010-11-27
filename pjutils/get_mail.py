#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, imaplib, rfc822
import string, re, StringIO

class GetMail():

    def get_imap(self, server_info, msg_id):
        M = imaplib.IMAP4_SSL(server_info['server'])
        M.login(server_info['username'], server_info['password'])
        M.select()
        messages = []
        typ, data = M.search(None, 'To', 'reply%s' % msg_id)
        for num in data[0].split():
            typ, data = M.fetch(num, '(RFC822)')

            file = StringIO.StringIO(data[0][1])

            message = rfc822.Message(file)

            mssg = message.fp.read()
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

    def get_mail(self, server_info, msg_id):
        messages = []
        if server_info['type'] == 'IMAP':
            messages = self.get_imap(server_info, msg_id)
        elif server_info['type'] == 'POP3':
            messages = self.get_pop3(server_info, msg_id)
        return messages

