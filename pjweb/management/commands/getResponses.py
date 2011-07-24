#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from pjutils.get_mail import GetMail
from pjutils.insert_response import InsertResponse
from pjweb.email.backends import MailHashIsNotCorrect, MailDoesNotExistInDBException
from settings import GlobalSettings
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
            'server':GlobalSettings.mail.IMAP.EMAIL_HOST,
            'port':GlobalSettings.mail.IMAP.EMAIL_PORT,
            'username':GlobalSettings.mail.IMAP.EMAIL_HOST_USER,
            'password':GlobalSettings.mail.IMAP.EMAIL_HOST_PASSWORD,
            'type':GlobalSettings.mail.IMAP.EMAIL_HOST_TYPE,
            'EMAIL_LOGIN_TYPE':GlobalSettings.mail.IMAP.EMAIL_LOGIN_TYPE
            }

        print "logging into mail server %s %s:%s" % (server_info['type'], server_info['server'], server_info['port'])
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

        if len(mailNumbers) == 0:
            print "No emails in server, exiting"
            return
        print "Will receive mails from %s to %s" % (fromNumber, toNumber)


        answered = 0


        skippedEmails = []
        deletedEmails = []
        responseEmails = []

        

        try:
            for num in mailNumbers[fromNumber:toNumber]:
                print "\n \nreading mail %s" % num
                # try to insert response
                # if an exception will be raised, leave this message, we will fix the bug and
                # insert it
                try:
                    email = getmail.readMessage(num)
                    if email is None:
                        print "could not extract email from message %s, skipping" % num
                        skippedEmails.append(num)
                        #print "marking message %s for deletion" % num
                        #getmail.markMessageForDeletion(num)
                        #deletedEmails.append(num)
                        continue
                    email_id, msg_text, msg_attachments = email
                    insert.insert_resp(email_id, msg_text, msg_attachments)
                except (MailHashIsNotCorrect, MailDoesNotExistInDBException) as e:
                    print e.message
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
