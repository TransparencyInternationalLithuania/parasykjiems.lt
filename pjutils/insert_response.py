#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pjutils.get_mail import GetMail
import settings
from settings import *
from django.core.management.base import BaseCommand
from parasykjiems.pjweb.models import Email, MailHistory
from django.core.mail import send_mail, EmailMessage
from cdb_lt_municipality.models import MunicipalityMember
from cdb_lt_mps.models import ParliamentMember
from cdb_lt_civilparish.models import CivilParishMember
from cdb_lt_seniunaitija.models import SeniunaitijaMember
from django.utils.encoding import smart_unicode

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

    def insert_response(self, mail_id):
        getmail = GetMail()
        resp = False
        if GlobalSettings.MAIL_SERVER:
            server_info = {
                'server':GlobalSettings.MAIL_SERVER,
                'port':GlobalSettings.MAIL_PORT,
                'username':GlobalSettings.MAIL_USERNAME,
                'password':GlobalSettings.MAIL_PASSWORD,
                'type':GlobalSettings.MAIL_SERVER_TYPE
            }
            mail = Email.objects.get(id=mail_id)
            responses = getmail.get_mail(server_info, mail_id, mail.response_hash)
            responder = self.get_rep(mail.recipient_id, mail.recipient_type)
            for response in responses:
                try:
                    message = unicode(response,'UTF-8')
                except:
                    message = unicode(response,'iso-8859-13')
                
                resp = Email(
                    sender_name = mail.recipient_name,
                    sender_mail = responder.email,
                    recipient_id = mail.recipient_id,
                    recipient_type = mail.recipient_type,
                    recipient_name = mail.sender_name,
                    recipient_mail = mail.sender_mail,
                    msg_type = 'Response',
                    response_hash = mail.response_hash,
                    answer_to = mail.id,
                    public = mail.public,
                )
                # if previous email was public, then we save the reply message text to db
                # else we delete it, and simply send whole email straight to the person
                # who asked the question in the first place
                if mail.public:
                    resp.message = message
                else:
                    resp.message = ''
                resp.save()

                # send a mail message to original person who asked a question.
                # Reply-to will not be an exact recipients email (resp.sender_mail),
                # but a "no_reply" address, meaning that we do not support "discussion" style
                # responses now.
                email = EmailMessage(u'Gavote atsakymą nuo %s' % resp.sender_name, response, settings.EMAIL_HOST_USER,
                    [resp.recipient_mail], [],
                    headers = {'Reply-To': 'no_reply_parasykjiems@gmail.com'})
                email.send()

            if resp:
                return resp
            else:
                return False
        return False

    def insert_resp(self, mail_info):
        resp = False
        mail = Email.objects.get(id=mail_info['msg_id'])
#        print mail.response_hash, mail_info['msg_hash']
        if mail.response_hash==int(mail_info['msg_hash']):
            responder = self.get_rep(mail.recipient_id, mail.recipient_type)
#            print responder
            resp = Email(
                sender_name = mail.recipient_name,
                sender_mail = responder.email,
                recipient_id = mail.recipient_id,
                recipient_type = mail.recipient_type,
                recipient_name = mail.sender_name,
                recipient_mail = mail.sender_mail,
                msg_type = 'Response',
                response_hash = mail.response_hash,
                answer_to = mail,
                public = mail.public,
            )
            # if previous email was public, then we save the reply message text to db
            # else we delete it, and simply send whole email straight to the person
            # who asked the question in the first place
            text = smart_unicode(mail_info['msg_text'], encoding=mail_info['msg_encoding'], strings_only=False, errors='strict')
            if mail.public:
                resp.message = text
            else:
                resp.message = ''

            if mail_info['filename']:
                web_path = '%s/%s' % (settings.ATTACHMENTS_MEDIA_PATH,mail_info['filename'])
                att_path = '%s/%s' % (settings.ATTACHMENTS_PATH,mail_info['filename'])
                resp.attachment_path = web_path

            resp.save()

            # send a mail message to original person who asked a question.
            # Reply-to will not be an exact recipients email (resp.sender_mail),
            # but a "no_reply" address, meaning that we do not support "discussion" style
            # responses now.
            email = EmailMessage(u'Gavote atsakymą nuo %s' % resp.sender_name, mail_info['msg_text'], settings.EMAIL_HOST_USER,
                [resp.recipient_mail], [],
                headers = {'Reply-To': 'no_reply_parasykjiems@gmail.com'})
            email.attach_file(att_path)
            email.send()

            if resp:
                return resp
            else:
                return False
        return False
