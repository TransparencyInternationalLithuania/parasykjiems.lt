#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import settings
from django.core.management.base import BaseCommand
from parasykjiems.pjutils.get_mail import GetMail
from parasykjiems.pjutils.insert_response import InsertResponse
from parasykjiems.pjweb.models import Email, MailHistory
from django.core.mail import send_mail, EmailMessage
from parasykjiems.GlobalSettingsClass import GlobalSettingsClass

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        responses_list = []
        questions_list = []
        waiting_list = []
        answered = 0
        server_info = {
            'server':settings.GlobalSettings.MAIL_SERVER,
            'port':settings.GlobalSettings.MAIL_PORT,
            'username':settings.GlobalSettings.MAIL_USERNAME,
            'password':settings.GlobalSettings.MAIL_PASSWORD,
            'type':settings.GlobalSettings.MAIL_SERVER_TYPE
        }
        getmail = GetMail()
        insert = InsertResponse()
        mail_list = getmail.get_mail(server_info)
        for email in mail_list:
            insert.insert_resp(email)
            answered += 1

        print "%s question got responses." % answered
