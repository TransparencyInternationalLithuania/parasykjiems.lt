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
        responses_list = []
        questions_list = []
        waiting_list = []
        questions = Email.objects.filter(msg_type__iexact='Question', msg_state__iexact='Confirmed')
        responses = Email.objects.filter(msg_type__iexact='Response')
        waiting = len(questions) - len(responses)
        print "%s questions are waiting for responses." % waiting
        for question in questions:
            questions_list.append(question.id)
        for response in responses:
            responses_list.append(response.answer_to)
        for question in questions_list:
            if not (question in responses_list):
                waiting_list.append(question)
        answered = 0
        waiting_list = list(set(waiting_list))
        print waiting_list
        insert = InsertResponse()
        if waiting_list:
            for question in waiting_list:
                response = insert.insert_response(question)
                if response:
                    answered += 1

        print "%s question got responses." % answered
