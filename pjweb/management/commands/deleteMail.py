#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from pjutils.get_mail import GetMail
from pjutils.insert_response import InsertResponse
from settings import GlobalSettings

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        """ Sometimes IMAP will get invalid emails.  use this to delete those unwanted emails"""

        server_info = {
            'server':GlobalSettings.MAIL_SERVER,
            'port':GlobalSettings.MAIL_PORT,
            'username':GlobalSettings.MAIL_USERNAME,
            'password':GlobalSettings.MAIL_PASSWORD,
            'type':GlobalSettings.MAIL_SERVER_TYPE
        }

        fromNumber, toNumber = ExtractRange(args[0])

        getmail = GetMail()
        getmail.login(server_info)
        insert = InsertResponse()
        mailNumbers = getmail.getUnseenMessages() + getmail.getSeenMessages()


        for num in mailNumbers:
            numInt = int(num)
            if numInt >= fromNumber and numInt < toNumber:
                print "deleting mail %s" % num
                getmail.markMessageForDeletion(num)



        # always logging out, and removing marked messages for deletion
        getmail.logout()
