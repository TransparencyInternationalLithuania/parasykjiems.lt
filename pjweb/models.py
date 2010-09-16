#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Email(models.Model):
    """ Table, where all emails are stored, and admin have to confirm them
    """
    
    MSG_STATES = (
        ('W', 'Waiting'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    
    EMAIL_STATES = (
        ('S', 'Sent'),
        ('N', 'Not Sent'),
        ('F', 'Failed Permanently'),
    )

    sender = models.EmailField()
    sender_name = models.CharField(max_length = 128)
    recipient = models.CharField(max_length = 255)
    message = models.TextField()
    phone = models.CharField(max_length = 100)
    msg_state = models.CharField(max_length=1, choices=MSG_STATES)
    email_state = models.CharField(max_length=1, choices=EMAIL_STATES)
    req_date = models.DateTimeField(auto_now = True)
    public = models.BooleanField()
