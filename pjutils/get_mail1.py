#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, imaplib, rfc822
import string, re, StringIO
import email
from email.charset import Charset
import quopri
import pprint

class GetMail():

    def get_imap(self, server_info):
# use IMAP4_SSL when SSL is supported on mail server
#        M = imaplib.IMAP4_SSL(server_info['server'])
# use login, when plaintext login is supported
#        M.login(server_info['username'], server_info['password'])
# use IMAP4 when SSL is not supported on mail server
        M = imaplib.IMAP4(server_info['server'], server_info['port'])
# use login_cram_md5(or some other supported login type) plaintext login is not supported
        M.login_cram_md5(server_info['username'], server_info['password'])
        code, mailboxen = M.list()
        M.select('INBOX')
        messages = []
        chrst = Charset()
        #insert_response = InsertResponse()
        typ, data = M.search(None, 'To', 'reply120_1223456')

        #typ, data = M.search(None, 'UNSEEN')

        messages_list = []

        for num in data[0].split():
            detach_dir = 'files'
            typ, msg_data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (To)])')
            to = msg_data[0][1].split('@')[0].replace('To: ','')
            if 'reply' in to:
                receiver = to.split('_')
                msg_id = receiver[0].replace('reply','')
                msg_hash = receiver[1]
                msg_text = ''
                att_path = ''
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

                        if not(part.get('Content-Disposition') is None):
                            filename = part.get_filename()
                            attachment_type = part.get_content_type()
                            content = part.get_payload()
                            counter = 1
                            print filename
                            print attachment_type
                            if not filename:
                                filename = 'part-%03d%s' % (counter, 'bin')
                                counter += 1
                            att_path = os.path.join(detach_dir, filename)
                            print att_path
                            if not os.path.isfile(att_path) :
                                # finally write the stuff
                                fp = open(att_path, 'wb')
                                fp.write(part.get_payload(decode=True))
                                fp.close()

                message_data = {'msg_id':msg_id,
                                'msg_hash':msg_hash,
                                'msg_text':msg_text,
                                'att_path':att_path}
                messages_list.append(message_data)

            else:
                M.store(num, '+FLAGS', '\\Deleted')

        print messages_list
        M.expunge()
        M.close()
        M.logout()
        #return messages

    def get_pop3(self, server_info):
        print 'Not yet implemented'
        return []

    def get_mail(self, server_info):
        messages = []
        if server_info['type'] == 'IMAP':
            messages = self.get_imap(server_info, msg_id, response_hash)
        elif server_info['type'] == 'POP3':
            messages = self.get_pop3(server_info, msg_id, response_hash)
        return messages
