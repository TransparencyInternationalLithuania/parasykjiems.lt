#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from contactdb.models import PersonPosition
from pjutils.exc import ChainedException
from pjutils.get_mail import GetMail
from pjweb.email.backends import MailDoesNotExistInDBException
import settings
from settings import GlobalSettings
from django.core.management.base import BaseCommand
from pjweb.models import Email, MailHistory
from django.core.mail import send_mail, EmailMessage


logger = logging.getLogger(__name__)

class InsertResponse():

    def get_rep(self, rep_id):
        try:
            return PersonPosition.objects.get(id=rep_id)
        except PersonPosition.DoesNotExist:
            return None

    def insert_resp(self, email_id, msg_text, msg_attachments):
        mail = None
        try:
            mail = Email.objects.get(id=email_id)
        except Email.DoesNotExist as e:
            raise MailDoesNotExistInDBException(message="We do not have email in database with id '%s'" % email_id, inner=e)

        responder = self.get_rep(mail.recipient_id)
        # print responder
        resp = Email(sender_name = mail.recipient_name,
                sender_mail = responder.email,
                recipient_id = mail.recipient_id,
                recipient_type = mail.recipient_type,
                recipient_name = mail.sender_name,
                recipient_mail = mail.sender_mail,
                msg_type = 'Response',
                response_hash = mail.response_hash,
                answer_to = mail,
                public = mail.public)
        # if previous email was public, then we save the reply message text to db
        # else we delete it, and simply send whole email straight to the person
        # who asked the question in the first place
        if mail.public:
            resp.message = msg_text
        else:
            resp.message = ''

        att_path = None
        attachments = msg_attachments
        if attachments is not None and len(attachments) > 0:
            # for now just handle single attachment only
            attachment = attachments[0]
            web_path = attachment[0]
            att_path = os.path.join(GlobalSettings.ATTACHMENTS_PATH,attachment[0])
            resp.attachment_path = web_path

        resp.save()


        from_email = GlobalSettings.mail.SMTP.REPRESENTATIVE_REPLY_EMAIl_SENT_FROM

        # send a mail message to original person who asked a question.
        # Reply-to will not be an exact recipients email (resp.sender_mail),
        # but a "no_reply" address, meaning that we do not support "discussion" style
        # responses now.
        email = EmailMessage(subject=u'Gavote atsakymą nuo %s' % resp.sender_name, body=msg_text, from_email=from_email,
            to=[resp.recipient_mail], bcc=[],
            headers = {'Reply-To': 'no_reply_parasykjiems@gmail.com'})
        if att_path is not None:
            email.attach_file(att_path)

        email.send()
