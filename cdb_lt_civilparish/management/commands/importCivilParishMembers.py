#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.imp import ImportSources, GoogleDocsSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
import logging
from cdb_lt_civilparish.models import CivilParishMember, CivilParish
from cdb_lt_civilparish.management.commands.importCivilParish import readRow

logger = logging.getLogger(__name__)

class ImportCivilParishMemberException(ChainnedException):
    pass

def toUnicode(str):
    return unicode(str, 'utf-8')

class CivilParishMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = ImportSources.Delimiter)


    def ReadMembers(self):
        for row in self.dictReader:
            member = CivilParishMember()
            member.name = readRow(row, "name")
            member.surname = readRow(row, "surname")
            member.email = row["officee-mail"]
            member.personalPhone = readRow(row, "personaltelephonenumber")
            member.officePhone = readRow(row, "officetelephonenumber")
            member.officeAddress = readRow(row, "officeaddress")
            member.civilParishStr = readRow(row, "institution")
            member.municipality= readRow(row, "municipality")
            member.uniqueKey = readRow(row, "uniquekeynotchangeable")

            yield member

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian CivilParishMembers / seniūnai'


    def alreadyExists(self, member):
        try:
            return CivilParishMember.objects.get(uniqueKey = member.uniqueKey)
        except ObjectDoesNotExist:
            return None


    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianCivilParishMembers)
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianCivilParishMembers)
        reader = CivilParishMembersReader(fileName)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        count = 0

        for member in reader.ReadMembers():

            if (member.name.strip() == ""):
                continue

            # check if already such member exists. Name and surname are primary keys
            m = self.alreadyExists(member)
            # relate existing constituency to an MP
            try:
                name = member.civilParishStr

                member.civilParish = CivilParish.objects.filter(name = name)\
                    .filter(municipality__icontains = member.municipality)[0:1].get()
            except ObjectDoesNotExist:
                str = u"""Parish with name '%s' could not be found in database table
%s while import CivilParishMembers. Data source taken from Google doc '%s'. Unique key '%s'  )""" % \
                    (name, CivilParish.objects.model._meta.db_table,
                    GoogleDocsSources.LithuanianCivilParishMembers, member.uniqueKey)
                logger.error(str)
                raise ImportCivilParishMemberException(str)

            if (m is None):
                print (u"Imported parish member %s %s %s" % (member.name, member.surname, member.civilParish.name))
                member.save()
            else:
                member.id = m.id
                print u"updating parish member: %s %s %s " % (m.name, m.surname, m.uniqueKey)
                member.save()


            count += 1
            if (count >= maxNumberToImport):
                break
        print u"succesfully imported/updated %d Parish Members" % (count)