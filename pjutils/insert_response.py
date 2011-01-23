#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from pjutils.exc import ChainnedException
from pjutils.get_mail import GetMail
import settings
from settings import GlobalSettings
from django.core.management.base import BaseCommand
from parasykjiems.pjweb.models import Email, MailHistory
from django.core.mail import send_mail, EmailMessage
from cdb_lt_municipality.models import MunicipalityMember
from cdb_lt_mps.models import ParliamentMember
from cdb_lt_civilparish.models import CivilParishMember
from cdb_lt_seniunaitija.models import SeniunaitijaMember
from django.utils.encoding import smart_unicode

logger = logging.getLogger(__name__)


class InsertResponseException(ChainnedException):
    pass

class MailDoesNotExistInDBException(InsertResponseException):
    pass

class MailHashIsNotCorrect(InsertResponseException):
    pass

class InsertResponse():

    def get_rep(self, rep_id, rtype):
        if rtype=='mp':
            receiver = ParliamentMember.objects.all().filter(
                    id__exact=rep_id
                )
        elif rtype=='mn':
            receiver = MunicipalityMember.objects.all().filter(
                    id__exact=rep_id
                )
        elif rtype=='cp':
            receiver = CivilParishMember.objects.all().filter(
                    id__exact=rep_id
                )
        elif rtype=='sn':
            receiver = SeniunaitijaMember.objects.all().filter(
                    id__exact=rep_id
                )

        return receiver[0]

    def insert_resp(self, mail_info):
        mail = None
        try:
            mail = Email.objects.get(id=mail_info['msg_id'])
        except Email.DoesNotExist as e:
            raise MailDoesNotExistInDBException(message="We do not have email in database with id '%s'" % mail_info['msg_id'], inner=e)

        # print mail.response_hash, mail_info['msg_hash']
        if mail.response_hash != int(mail_info['msg_hash']):
            params = (mail_info['msg_id'], mail.response_hash, mail_info['msg_hash'])
            raise MailHashIsNotCorrect(message="Hash for mail '%s' was not correct. It should be '%s', but was '%s'" % params)

        responder = self.get_rep(mail.recipient_id, mail.recipient_type)
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
        #text = SmartUnicode(mail_info['msg_text'])
        #text = unicode(mail_info['msg_text'], 'utf-8')
        text = smart_unicode(mail_info['msg_text'], encoding=mail_info['msg_encoding'], strings_only=False, errors='strict')
        if mail.public:
            resp.message = text
        else:
            resp.message = ''

        att_path = None
        attachments = mail_info["attachments"]
        if attachments is not None and len(attachments) > 0:
            # for now just handle single attachment only
            attachment = attachments[0]
            web_path = attachment[0]
            att_path = os.path.join(GlobalSettings.ATTACHMENTS_PATH,attachment[0])
            resp.attachment_path = web_path

        resp.save()

        # send a mail message to original person who asked a question.
        # Reply-to will not be an exact recipients email (resp.sender_mail),
        # but a "no_reply" address, meaning that we do not support "discussion" style
        # responses now.
        email = EmailMessage(u'Gavote atsakymą nuo %s' % resp.sender_name, mail_info['msg_text'], settings.EMAIL_HOST_USER,
            [resp.recipient_mail], [],
            headers = {'Reply-To': 'no_reply_parasykjiems@gmail.com'})
        if att_path is not None:
            email.attach_file(att_path)

        email.send()