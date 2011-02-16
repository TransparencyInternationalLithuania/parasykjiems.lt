#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from django.core.management.base import BaseCommand
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from pjutils.get_mail import GetMail
from pjutils.insert_response import InsertResponse
from settings import GlobalSettings

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        """ Sometimes IMAP will get invalid emails.  use this to read those unwanted emails"""

        server_info = {
            'server':GlobalSettings.mail.IMAP.EMAIL_HOST,
            'port':GlobalSettings.mail.IMAP.EMAIL_PORT,
            'username':GlobalSettings.mail.IMAP.EMAIL_HOST_USER,
            'password':GlobalSettings.mail.IMAP.EMAIL_HOST_PASSWORD,
            'type':GlobalSettings.mail.IMAP.EMAIL_HOST_TYPE,
            'EMAIL_LOGIN_TYPE':GlobalSettings.mail.IMAP.EMAIL_LOGIN_TYPE
            }

        getmail = GetMail()
        getmail.login(server_info)
        insert = InsertResponse()
        mailNumbers = getmail.getUnseenMessages() + getmail.getSeenMessages()

        print "there are these emails: %s" % mailNumbers
        if len(args) < 1:
            print "Use this command to read emails. Specify emails by comman (no spaces), or as a python range"
            return

        emailsToRead = []

        if args[0].find(':') >= 0:
            fromNumber, toNumber = ExtractRange(args[0])
            for num in mailNumbers:
                numInt = int(num)
                if numInt >= fromNumber and numInt < toNumber:
                    emailsToRead.append(numInt)
        elif args[0].find(',') >= 0:
            for p in args[0].split(','):
                emailsToRead.append(int(p))
        else:
            try:
                emailsToRead.append(int(args[0]))
            except ValueError:
                print "incorrect argument passed %s" % args[0]
                return



        print "will read emails %s" %emailsToRead
        
        for num in emailsToRead:
            print "reading mail %s" % num
            dataRaw = getmail.readMail(num)
            data = dataRaw[0][1]
            print data



        # always logging out, and removing marked messages for deletion
        getmail.logout()
