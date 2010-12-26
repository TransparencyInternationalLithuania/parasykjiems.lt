#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import settings
from settings import *
from django.core.management.base import BaseCommand
from parasykjiems.pjutils.get_mail import GetMail
from parasykjiems.pjweb.models import Email, MailHistory
from django.core.mail import send_mail, EmailMessage
from cdb_lt_municipality.models import MunicipalityMember
from cdb_lt_mps.models import ParliamentMember
from cdb_lt_civilparish.models import CivilParishMember
from cdb_lt_seniunaitija.models import SeniunaitijaMember

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
                if mail.public:
                    mail.message = message
                else:
                    mail.message = ''
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
