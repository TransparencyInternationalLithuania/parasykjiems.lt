#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import os, sys, imaplib, rfc822
import string, re, StringIO
import email
from pjutils.exc import MethodNotImplementedException
import settings
from distutils import dir_util

logger = logging.getLogger(__name__)

class GetMail():

    def get_imap(self, server_info):
        # use IMAP4_SSL when SSL is supported on mail server
        # M = imaplib.IMAP4_SSL(server_info['server'])
        # use login, when plaintext login is supported
        # M.login(server_info['username'], server_info['password'])
        # use IMAP4 when SSL is not supported on mail server
        M = imaplib.IMAP4(server_info['server'], server_info['port'])
        
        # use login_cram_md5(or some other supported login type) plaintext login is not supported
        M.login_cram_md5(server_info['username'], server_info['password'])

        M.select('INBOX')
        
        # we will check all new messages
        typ, data = M.search(None, 'UNSEEN')

        messages_list = []

        for num in data[0].split():
            detach_dir = settings.ATTACHMENTS_PATH
            typ, msg_data = M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (To)])')
            to = msg_data[0][1].split('@')[0].replace('To: ','')
            if 'reply' in to:
                receiver = to.split('_')
                msg_id = receiver[0].replace('reply','')
                msg_hash = receiver[1]
                msg_text = ''
                filename = ''
                msg_encoding = ''
                filename = ""
                typ, msg_data = M.fetch(num, '(RFC822)')
                for response_part in msg_data:

                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])
                        # if message is multipart...
                        if msg.is_multipart():
                            for part in msg.walk():
                                # we will take only plain text...
                                if part.get_content_type() == 'text/plain':
                                    msg_encoding = part.get_param('charset')
                                    msg_text = part.get_payload().decode('quoted-printable')
                        else:
                            msg_text = msg.get_payload().decode('quoted-printable')

                        # and attachment
                        if not(part.get('Content-Disposition') is None):
                            filename = part.get_filename()
                            attachment_type = part.get_content_type()
                            content = part.get_payload()
                            counter = 1
                            if not filename:
                                filename = 'part-%03d%s' % (counter, 'bin')
                                counter += 1
                            dir_util.mkpath(detach_dir)
                            att_path = os.path.join(detach_dir, filename)
                            if not os.path.isfile(att_path) :
                                # finally write the stuff
                                fp = open(att_path, 'wb')
                                fp.write(part.get_payload(decode=True))
                                fp.close()

                message_data = {'msg_id':msg_id,
                                'msg_hash':msg_hash,
                                'msg_text':msg_text,
                                'msg_encoding':msg_encoding,
                                'filename':filename}
                messages_list.append(message_data)

            else:
                M.store(num, '+FLAGS', '\\Deleted')

        M.expunge()
        M.close()
        M.logout()
        return messages_list

    def get_pop3(self, server_info):
        logger.info('Not yet implemented')
        raise MethodNotImplementedException("get_pop3 is not yet implemented")

    def get_mail(self, server_info):
        messages = []
        if server_info['type'] == 'IMAP':
            messages = self.get_imap(server_info)
        elif server_info['type'] == 'POP3':
            messages = self.get_pop3(server_info)
        return messages
