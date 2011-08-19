#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from optparse import make_option
from django.core.management.base import BaseCommand
from pjutils.get_mail import GetMail
from settings import GlobalSettings

class Command(BaseCommand):
    args = '<>'
    help = ''


    option_list = BaseCommand.option_list + (
        make_option('-f', '--from',
            dest='from',
            metavar="from",
            default = "",
            help='Specify what from address should look like. Will do a contains query'),
        )


    def handle(self, *args, **options):
        """ Sometimes IMAP will get invalid emails.  use this to delete those unwanted emails.
        Use options to tell which emails you want to delet"""

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
        mailNumbers = getmail.getUnseenMessages() + getmail.getSeenMessages()

        print "there are these emails: %s" % mailNumbers


        fromEmail =  options['from']

        if fromEmail.strip() == u"":
            print "Did not specify --from option, exiting"
            return

        print "will delete emails where from %s" % fromEmail
        seconds = 5
        print "Is that ok? Will wait for %s seconds" % seconds
        time.sleep(seconds)

        for num in mailNumbers:
            fr = getmail.getHeaderFieldFrom(num)
            print "%s email from: '%s'" % (num, fr)
            if fr.find(fromEmail) >= 0:
                print "deleting mail %s" % num
                getmail.markMessageForDeletion(num)



        # always logging out, and removing marked messages for deletion
        getmail.logout()
