#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import settings
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
        if settings.MAIL_SERVER:
            server_info = {
                'server':settings.MAIL_SERVER,
                'port':settings.MAIL_PORT,
                'username':settings.MAIL_USERNAME,
                'password':settings.MAIL_PASSWORD,
                'type':settings.MAIL_SERVER_TYPE
            }
            mail = Email.objects.get(id=mail_id)

            responses = getmail.get_mail(server_info, mail_id, mail.response_hash)
            responder = self.get_rep(mail.recipient_id, mail.recipient_type)

            for response in responses:
                message = response
                sender = responder.email
                recipients = mail.sender_mail
                resp = response.split('>\r')
                response_1 = ''.join(resp)
                lines = response_1.split('\n')
                for line in lines:
                    find_us = line.find('parasykjiems@gmail.com')
                    if len(line)>0 and (line[0]=='>' or find_us>-1):
                        #print len(line), line
                        lines.remove(line)
                message_1 = '\n'.join(lines)
                resp = Email(
                    sender_name = mail.recipient_name,
                    sender_mail = responder.email,
                    recipient_id = mail.recipient_id,
                    recipient_type = mail.recipient_type,
                    recipient_name = mail.sender_name,
                    recipient_mail = mail.sender_mail,
                    message = message_1,
                    msg_state = 'R',
                    response_hash = mail.response_hash,
                    answer_to = mail.id,
                    public = True,
                )
                resp.save()

                email = EmailMessage(u'Gavote atsakymą nuo %s' % resp.sender_name, response, 'parasykjiems@gmail.com',
                    [resp.recipient_mail], [],
                    headers = {'Reply-To': resp.sender_mail})
                email.send()

                email_edit = Email(
                    id = mail.id,
                    sender_name = mail.sender_name,
                    sender_mail = mail.sender_mail,
                    recipient_id = mail.recipient_id,
                    recipient_type = mail.recipient_type,
                    recipient_name = mail.recipient_name,
                    recipient_mail = mail.sender_mail,
                    message = mail.message,
                    msg_state = 'A',
                    response_hash = mail.response_hash,
                    answer_to = mail.answer_to,
                    public = mail.public,
                )
                email_edit.save()
                mail_history = MailHistory(
                    sender = mail.sender_mail,
                    recipient = mail.recipient_mail,
                    mail = mail,
                    mail_state = 'A',
                )
                mail_history.save()
            if resp:
                return resp
            else:
                return False
        return False
