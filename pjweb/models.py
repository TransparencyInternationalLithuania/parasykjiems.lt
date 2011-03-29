#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Email(models.Model):
    """ Table, where all emails are stored
    """
    
    MSG_STATES = (
        ('NotConfirmed', 'Not Confirmed'),
        ('Confirmed', 'Confirmed'),
    )

    MSG_TYPES = (
        ('Question', 'Question'),
        ('Response', 'Response'),
    )

    sender_mail = models.EmailField()
    sender_name = models.CharField(max_length = 128)
    recipient_name = models.CharField(max_length = 128)
    recipient_id = models.IntegerField()
    recipient_type = models.CharField(max_length = 50)
    recipient_mail = models.EmailField()

    " a relation to previous email, to which this email is an answer"
    answer_to = models.ForeignKey('Email',null=True)
    response_hash = models.IntegerField()
    message = models.TextField(blank=True)
    msg_state = models.CharField(max_length=12, choices=MSG_STATES, null=True)
    msg_type = models.CharField(max_length=10, choices=MSG_TYPES, null=True)
    mail_date = models.DateTimeField(auto_now=True, editable=False)
    attachment_path = models.CharField(max_length=256, null=True)
    public = models.BooleanField()

    def __unicode__(self):
        return self.recipient_name

class MailHistory(models.Model):
    """ It will show, what was done with an email
    """

    EMAIL_STATES = (
        ('Sent', 'Sent'),
        ('FailedPermanently', 'Failed Permanently'),
        ('Failed', 'Failed'),
    )

    sender = models.EmailField()
    recipient = models.CharField(max_length = 128)
    mail = models.ForeignKey('Email')
    mail_state = models.CharField(max_length=17, choices=EMAIL_STATES, blank=True)
    request_date = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.sender
