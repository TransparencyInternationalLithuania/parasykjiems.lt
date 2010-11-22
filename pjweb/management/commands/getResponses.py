#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import settings
from django.core.management.base import BaseCommand
from parasykjiems.pjutils.get_mail import GetMail
from parasykjiems.pjutils.insert_response import InsertResponse
from parasykjiems.pjweb.models import Email, MailHistory
from django.core.mail import send_mail, EmailMessage

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        responses = []
        requests = Email.objects.filter(msg_state__exact='W')
        waiting = len(requests)
        print "%s requests are waiting for responses." % waiting
        answered = 0
        insert = InsertResponse()
        if requests:
            for request in requests:
                response = insert.insert_response(request.id)
                if response:
                    answered += 1

        print "%s mails got answers." % answered
