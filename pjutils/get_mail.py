#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

import os, sys, imaplib, rfc822
import string, re, StringIO
import email
from pjutils.exc import MethodNotImplementedException, ChainnedException
from settings import *

logger = logging.getLogger(__name__)

class EmailPlainTextPartNotFound(ChainnedException):
    pass

class MailPartException(ChainnedException):
    pass

class AttachmentAlreadyExistsException(ChainnedException):
    pass

class IMAPException(ChainnedException):
    pass

class GetMail():

    def login(self, server_info):
        if server_info['type'] != 'IMAP':
            raise MethodNotImplementedException("Server type %s is not yet implemented" % server_info['type'])

        # use IMAP4_SSL when SSL is supported on mail server
        # M = imaplib.IMAP4_SSL(server_info['server'])
        # use login, when plaintext login is supported
        # M.login(server_info['username'], server_info['password'])
        # use IMAP4 when SSL is not supported on mail server
        self.M = imaplib.IMAP4(server_info['server'], server_info['port'])

        # use login_cram_md5(or some other supported login type) plaintext login is not supported
        self.M.login_cram_md5(server_info['username'], server_info['password'])

        self.M.select('INBOX')

    def logout(self):
        self.M.expunge()
        self.M.close()
        self.M.logout()
        

    def getEmailTextAndEncodingAndAttachments(self, msg_id, msg):
        """ msg_id is the email number in IMAP server. used only for logging.
        msg is the message object"""
        msg_encoding = msg.get_content_charset()

        # if message is not multipart, just decode everything using QP encoding
        # see more: http://en.wikipedia.org/wiki/Quoted-printable
        if not msg.is_multipart():
            msg_text = msg.get_payload().decode('quoted-printable')
            return msg_text, msg_encoding, []


        attachment_count = 0
        attachments = []
        # Else walk through every part of this response part
        # Probably, one part will be text/plain, another will be html, or any other.
        # Just take plain text from that
        for part in msg.walk():
            # we will take only plain text...
            if part.get_content_type() == 'text/plain':
                # this part is plain text, so extract and return
                msg_encoding = part.get_param('charset')
                msg_text = part.get_payload().decode('quoted-printable')
                continue
        
            # and attachment
            contentDisposition = part.get('Content-Disposition')
            if contentDisposition is not None:
                attachment_count += 1
                attachment_type = part.get_content_type()
                filename = part.get_filename()
                if not filename:
                    filename = 'part-%s.%s' % (attachment_count, 'bin')

                # create folder for an attachment
                year = "%s" % datetime.datetime.now().year
                att_path = os.path.join(GlobalSettings.ATTACHMENTS_PATH, year, msg_id)
                att_fileName = os.path.join(att_path, filename)
                dir_util.mkpath(att_path)

                # check if we are not overwriting old attachment
                if os.path.isfile(att_path):
                    raise AttachmentAlreadyExistsException(message= "attachment at location '%s' already exists. msg num is '%s'" % (att_fileName, msg_id))
                # finally write the stuff
                fp = open(att_fileName, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

                attachments.append((att_fileName, attachment_type))

        if msg_text is None:
            # we did not find text/plain section, raise exception
            raise EmailPlainTextPartNotFound(message="We could not find text/plain section in this email")

        return msg_text, msg_encoding, attachments


    def getHeaderReceived(self, num):
        typ, msg_data = self.M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (Received)])')
        headers = msg_data[0][1]
        return headers

    def getHeaderFieldTo(self, num):
        typ, msg_data = self.M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (To)])')
        headers = msg_data[0][1].split("\r\n")
        return headers[0].split('@')[0].replace('To: ','')

    def getHeaderFieldFrom(self, num):
        typ, msg_data = self.M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (From)])')
        headers = msg_data[0][1].split("\r\n")
        split = headers[0].split('From: ')
        if len(split) < 2:
            return ""
        return split[1]

    def getHeaderFieldSubject(self, num):
        typ, msg_data = self.M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (Subject)])')
        headers = msg_data[0][1].split("\r\n")
        split = headers[0].split('Subject: ')
        if len(split) < 2:
            return ""
        return split[1]


    def getUnseenMessages(self):
        typ, data = self.M.search(None, 'UNSEEN')
        if typ != "OK":
            raise IMAPException(message="response from imap was %s" % typ)
        return data[0].split()

    def getSeenMessages(self):
        typ, data = self.M.search(None, 'SEEN')
        if typ != "OK":
            raise IMAPException(message="response from imap was %s" % typ)
        return data[0].split()

    def markMessageForDeletion(self, num):
        self.M.store(num, '+FLAGS', '\\Deleted')


    def readMessage(self, num):
        """ Will read message from IMAP. message num is passed as argument.
        Use getUnseenMessages or getSeenMessages to get a list of mails.

        Will return None if message is a spam, or does not contain correct header.
        Otherwise will extract text, encoding, and save attachments to disk,
        and will return this data. See code for details"""

        header_to = self.getHeaderFieldTo(num)
        header_from = self.getHeaderFieldFrom(num)
        header_subject = self.getHeaderFieldSubject(num)
        header_received = self.getHeaderReceived(num).strip("\r\n")


        print ("Got email num %s \n \t from: %s \n \t To: %s \n \t Subject: %s \n \t Received: %s") % (num, header_from, header_to, header_subject, header_received)

        # if to: field does not contain our defined mail prefix
        # delete the email, and continue processing other mails
        if GlobalSettings.DefaultMailPrefix not in header_to:
            print "Email %s did not have correct header, either spam, or some other email" % num
            return None


        # extract everything and process mail
        return self.fetchAndParseMail(num, header_to)


    def fetchAndParseMail(self, num, header_to):

        receiver = header_to.split('_')
        msg_id = receiver[0].replace('reply','')
        msg_hash = receiver[1]
        msg_text = ''
        filename = ""
        typ, msg_data = self.M.fetch(num, '(RFC822)')

        # for some reason msg_date is always len of 2. first element is tuple
        # second element is left parenthesis
        if len(msg_data) != 2:
            raise MailPartException(message= "there was more than 2 mail parts. actually, there was %s parts" % len(msg_data))
        response_part = msg_data[0]
        if not isinstance(response_part, tuple):
            raise MailPartException(message= "response_part should be a tuple. instead, it was %s" % type(response_part))

        # convert to message object
        msg = email.message_from_string(response_part[1])

        # extract text, encoding and attachments
        msg_text, msg_encoding, msg_attachments = self.getEmailTextAndEncodingAndAttachments(num, msg)


        message_data = {'msg_id':msg_id,
                        'msg_hash':msg_hash,
                        'msg_text':msg_text,
                        'msg_encoding':msg_encoding,
                        'attachments':msg_attachments}
        return message_data
