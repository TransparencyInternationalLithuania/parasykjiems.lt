    #!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

import os, sys, imaplib, rfc822
import string, re, StringIO
import email
from pjutils.exc import MethodNotImplementedException, ChainedException
from pjweb.email.backends import CanNotExtractEmailIdAndHash
from settings import *
from django.utils.encoding import smart_unicode

logger = logging.getLogger(__name__)

class EmailPlainTextPartNotFound(ChainedException):
    pass

class MailPartException(ChainedException):
    pass

class AttachmentAlreadyExistsException(ChainedException):
    pass

class IMAPException(ChainedException):
    pass

class GetMail():

    def login(self, server_info):
        serverType = server_info['type']
        if serverType == 'IMAP':
            # use IMAP4_SSL when SSL is supported on mail server
            # M = imaplib.IMAP4_SSL(server_info['server'])
            # use login, when plaintext login is supported
            # M.login(server_info['username'], server_info['password'])
            # use IMAP4 when SSL is not supported on mail server
            self.M = imaplib.IMAP4(server_info['server'], server_info['port'])
        elif serverType == 'IMAP4_SSL':
            self.M = imaplib.IMAP4_SSL(server_info['server'], server_info['port'])
        else:
            raise MethodNotImplementedException("Server type %s is not yet implemented" % server_info['type'])

        loginType = server_info['EMAIL_LOGIN_TYPE']
        if loginType == "PLAIN":
            self.M.login(server_info['username'], server_info['password'])
        elif loginType == "CRAM_MD5":
            # use login_cram_md5(or some other supported login type) plaintext login is not supported
            self.M.login_cram_md5(server_info['username'], server_info['password'])
        else:
            raise MethodNotImplementedException("EMAIL_LOGIN_TYPE  %s is not yet implemented" % loginType)


        self.M.select('INBOX')



    def logout(self):
        self.M.expunge()
        self.M.close()
        self.M.logout()

    def getNewAttachmentName(self, fullDir, fileName):
        att_fileName = os.path.join(fullDir, fileName)
        if not os.path.isfile(att_fileName):
            return fileName

        fileName, extension = os.path.splitext(fileName)
        i = 1
        while True:
            f = u"%s-%s%s" % (fileName, i, extension)
            att_fileName = os.path.join(fullDir, f )
            if not os.path.isfile(att_fileName):
                return f
            i += 1
        raise AttachmentAlreadyExistsException(message= "attachment at location '%s' already exists" % fileName)

    def getEmailTextAndEncodingAndAttachments(self, msg_id, msg):
        """ msg_id is email number in our database. used only for logging and creating directory for attachments
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
                msg_encoding = part.get_content_charset()
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
                msg_id = u"%s" % msg_id
                fullDir = os.path.join(GlobalSettings.ATTACHMENTS_PATH, year, msg_id)
                dir_util.mkpath(fullDir)
                

                # check if we are not overwriting old attachment. get a new filename if necessary
                filename = self.getNewAttachmentName(fullDir, filename)

                # construct final path
                att_fileName = os.path.join(fullDir, filename)
                
                # finally write the stuff
                fp = open(att_fileName, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

                # return relative file path, and attachment type
                relativeFilePath = os.path.join(year, msg_id, filename)
                attachments.append((relativeFilePath, attachment_type))

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
        r = headers[0].split('@')[0].replace('To: ','')
        r = r.strip('<')
        return r

    def getHeaderFieldFrom(self, num):
        typ, msg_data = self.M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (From)])')
        headers = msg_data[0][1].split("\r\n")
        split = headers[0].split('From: ')
        if len(split) < 2:
            return ""
        return split[1]

    def _splitHeader(self, header):
        result = [header]
        while True:
            fromIndex = header.find("=?")
            toIndex = header.find("?=") + 2
            if fromIndex < 0:
                break
            extract = header[fromIndex: toIndex]
            header = "%s----%s" % (header[0:fromIndex], header[toIndex:])
            result.append(extract)
        header = header.replace("----", "%s")
        result[0] = header
        return result

    def _rebuildEncodeHeader(self, sheader):
        for i in range(1, len(sheader)):
            s = sheader[i]
            x = email.header.decode_header(s)
            s1 = x[0][0].decode(x[0][1])
            sheader[i] = s1

        tupl = tuple(sheader[1:])
        finalHeader = sheader[0] % tupl
        return finalHeader


    def _decodeHeader(self, header):
        # seee http://stackoverflow.com/questions/5343191/how-does-encoding-in-email-subjects-work-django-python
        sheader = self._splitHeader(header)
        h = self._rebuildEncodeHeader(sheader)
        return h


    def getHeaderFieldSubject(self, num):
        typ, msg_data = self.M.fetch(num, '(BODY.PEEK[HEADER.FIELDS (Subject)])')
        s = msg_data[0][1]
        return self._decodeHeader(s)



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


    def readMail(self, num):
        typ, msg_data = self.M.fetch(num, '(RFC822)')
        return msg_data

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


        # check if a message id can be extracted from this email
        email_id = None
        for composition_backend in GlobalSettings.mail.composition_backends:
            try:
                email_id = composition_backend.getEmailId(header_to = header_to, header_from=header_from, header_subject=header_subject, header_received = header_received)
            except CanNotExtractEmailIdAndHash:
                continue
        if email_id is None:
            return None

        # extract everything and process mail
        msg_text, msg_encoding, msg_attachments = self.fetchAndParseMail(num, email_id)
        msg_text = smart_unicode(msg_text, encoding=msg_encoding, strings_only=False, errors='strict')
        return email_id, msg_text, msg_attachments


    def fetchAndParseMail(self, num, email_id):
        msg_data = self.readMail(num)

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
        msg_text, msg_encoding, msg_attachments = self.getEmailTextAndEncodingAndAttachments(email_id, msg)
        return msg_text, msg_encoding, msg_attachments
