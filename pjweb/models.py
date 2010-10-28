#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Email(models.Model):
    """ Table, where all emails are stored, and admin have to confirm them
    """
    
    MSG_STATES = (
        ('W', 'Waiting'),
        ('A', 'Answered'),
        ('R', 'Response'),
    )
    
    EMAIL_STATES = (
        ('C', 'Confirmed'),
        ('N', 'Not Confirmed'),
    )
    
    MSG_TYPE = (
        ('M', 'Message'),
        ('R', 'Response'),
    )

    sender = models.EmailField()
    sender_name = models.CharField(max_length = 128)
    recipient_name = models.CharField(max_length = 128)
    recipient_id = models.IntegerField()
    recipient_type = models.CharField(max_length = 5)
    answer_no = models.IntegerField()
    message = models.TextField()
    phone = models.CharField(max_length = 100)
    msg_state = models.CharField(max_length=1, choices=MSG_STATES)
    email_state = models.CharField(max_length=1, choices=EMAIL_STATES, blank=True)
    msg_type = models.CharField(max_length=1, choices=MSG_TYPE)
    req_date = models.DateTimeField(auto_now = True)
    public = models.BooleanField()

