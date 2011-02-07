#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
from cdb_lt_seniunaitija.models import Seniunaitija, SeniunaitijaMember
from cdb_lt_civilparish.management.commands.importCivilParishMembers import ImportCivilParishMemberException
from cdb_lt_civilparish.management.commands.importCivilParish import readRow

class ImportSeniunaitijaMemberException(ChainnedException):
    pass

class SeniunaitijaMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = ImportSources.Delimiter)

    def ReadMembers(self):
        for row in self.dictReader:
            member = SeniunaitijaMember()
            member.name = readRow(row, "name")
            member.surname = readRow(row, "surname")
            member.email = readRow(row, "e-mail")
            member.phone = readRow(row, "telephonenumber")
            member.homePhone = readRow(row, "hometelephonenumber")
            member.role = readRow(row, "pareigos")
            member.seniunaitijaStr = readRow(row, "seniunaitija")
            member.municipalityStr = readRow(row, "municipality")
            member.civilParishStr = readRow(row, "townshipseniunija")
            member.territoryStr = readRow(row, "territorycoveredbyseniunaitija")
            member.uniqueKey = int(readRow(row, "uniquekeynotchangeable"))
            yield member

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian SeniunaitijaMember  / seniūnaičiai'

    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianSeniunaitijaMembers)
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)
        reader = SeniunaitijaMembersReader(fileName)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        count = 0

        for member in reader.ReadMembers():

            if (member.name.strip() == ""):
                print u"member name was empty. "
                print u"Probably that means that in seniunaitija %s a member was not yet elected" % member.seniunaitijaStr
                continue


            # relate existing seniunaitija to seniūnaitis
            try:
                name = member.seniunaitijaStr
                member.institution = Seniunaitija.objects.filter(id = member.uniqueKey)[0:1].get()
            except ObjectDoesNotExist:
                raise ImportCivilParishMemberException("""Seniunaitija with name '%s' and type '%s' could not be found in database. Either the database is
not yet populated with seniunaitija, or it is missing (probably because import data does not contain it)""" % \
                    (name, type))

            member.id = member.uniqueKey
            member.save()
            print "Seniunaitija member: %s %s %s" % (member.uniqueKey, member.name, member.surname)


            count += 1
            if (count >= maxNumberToImport):
                break
        print u"succesfully imported %d seniunaitija members" % (count)