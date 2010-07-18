#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

class Emails(models.Model):
    """ Table, where all emails are stored, and admin have to confirm them
    """
    
    EMAIL_STATES = (
        ('W', 'Waiting'),
        ('A', 'Approved'),
        ('S', 'Sent'),
    )
    
    sender = models.EmailField()
    sender_name = models.CharField(max_length = 128)
    recipient = models.CharField(max_length = 255)
    message = models.TextField()
    subject = models.CharField(max_length = 100)
    state = models.CharField(max_length=1, choices=EMAIL_STATES)