#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from pjutils.get_mail import GetMail
from pjutils.insert_response import MailHashIsNotCorrect, InsertResponse, MailDoesNotExistInDBException
from settings import GlobalSettings
import sys
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        """ Will scan IMAP server and search for valid emails. Valid emails are those,
        which have a standard header, i.e. start with a common prefix, have a mail id and a hash.
        Non valid emails will be marked for deletion immediatelly.
        Valid emails will be yielded for immediate processing."""

        server_info = {
            'server':GlobalSettings.MAIL_SERVER,
            'port':GlobalSettings.MAIL_PORT,
            'username':GlobalSettings.MAIL_USERNAME,
            'password':GlobalSettings.MAIL_PASSWORD,
            'type':GlobalSettings.MAIL_SERVER_TYPE
            }

        getmail = GetMail()
        getmail.login(server_info)
        insert = InsertResponse()
        mailNumbers = getmail.getUnseenMessages() + getmail.getSeenMessages()

        fromNumber = 0
        toNumber = None
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])
        if toNumber is None:
            toNumber = len(mailNumbers)
        print "Will receive mails from %s to %s" % (fromNumber, toNumber)


        answered = 0


        skippedEmails = []
        deletedEmails = []
        responseEmails = []

        

        try:
            for num in mailNumbers[fromNumber:toNumber]:
                print "\n \nreading mail %s" % num
                email = getmail.readMessage(num)
                if email is None:
                    print "marking message %s for deletion" % num
                    getmail.markMessageForDeletion(num)
                    deletedEmails.append(num)
                    continue
                # try to insert response
                # if an exception will be raised, leave this message, we will fix the bug and
                # insert it
                try:
                    insert.insert_resp(email)
                except MailHashIsNotCorrect as e:
                    print e.message
                    skippedEmails.append(num)
                    continue
                except MailDoesNotExistInDBException as ex:
                    print ex.message
                    skippedEmails.append(num)
                    continue

                print "message imported succesfully. deleting original"
                getmail.markMessageForDeletion(num)
                responseEmails.append(num)
                answered += 1
        finally:
            # always logging out, and removing marked messages for deletion
            getmail.logout()

        print "\n\n"
        print "quitting"
        print "following emails were skipped because of error: %s" % skippedEmails
        print "following emails were deleted (spam, or incorrect header): %s" % deletedEmails
        print "following emails were imported succesfully: %s" % responseEmails
        print "%s question got responses." % answered
