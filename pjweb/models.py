#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Email(models.Model):
    """ Table, where all emails are stored
    """
    
    MSG_STATES = (
        ('N', 'Not Confirmed'),
        ('W', 'Waiting'),
        ('A', 'Answered'),
        ('R', 'Response'),
    )

    sender_mail = models.EmailField()
    sender_name = models.CharField(max_length = 128)
    recipient_name = models.CharField(max_length = 128)
    recipient_id = models.IntegerField()
    recipient_type = models.CharField(max_length = 5)
    recipient_mail = models.EmailField()
    answer_to = models.IntegerField(null=True)
    response_hash = models.IntegerField()
    message = models.TextField(blank=True)
    msg_state = models.CharField(max_length=1, choices=MSG_STATES)
    mail_date = models.DateTimeField(auto_now=True, editable=False)
    public = models.BooleanField()

    def __unicode__(self):
        return self.recipient_name

class MailHistory(models.Model):
    """ It will show, what was done with an email
    """

    EMAIL_STATES = (
        ('C', 'Confirmed'),
        ('S', 'Sent'),
        ('N', 'New'),
        ('F', 'Failed'),
    )

    sender = models.EmailField()
    recipient = models.CharField(max_length = 5)
    mail = models.ForeignKey('Email')
    mail_state = models.CharField(max_length=1, choices=EMAIL_STATES, blank=True)
    request_date = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.sender
