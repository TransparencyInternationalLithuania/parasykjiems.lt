#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
from contactdb.imp import GoogleDocsSources, ImportSources
import logging
from cdb_lt_seniunaitija.models import Seniunaitija
from cdb_lt_civilparish.management.commands.importCivilParish import readRow

logger = logging.getLogger(__name__)


class SeniunaitijaStreetParser:

    def GetStreets(self, streetStr):
        str = streetStr.split(',')

        for s in str:
            yield s.strip()


class ImportSeniunaitijaException(ChainnedException):
    pass

class SeniunaitijaNotFoundException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian Seniunaitija / seniūnaitijos'

    def FixNames(self):
        # remove some keywords from strings, and add others
        # this is to conform to a de-facto data naming standard
        self.municipalityStr = self.municipalityStr.replace("rajono", "").strip()

        # if it is not an UAB / LTD company
        if (self.civilParishStr.find(u'UAB') < 0):
            # add a kewyword "seniūnija" unless it is already there
            if (self.civilParishStr.find(u"seniūnija") < 0):
                self.civilParishStr = u"%s seniūnija" % self.civilParishStr


    @transaction.commit_on_success
    def handle(self, *args, **options):
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        parser = SeniunaitijaStreetParser()

        count = 0
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = ImportSources.Delimiter)

        for row in self.dictReader:
            # i use class instance variables here on purpose. Might be tricky if the class grows too much,
            # but handy for now

            self.seniunaitijaStr = readRow(row, "seniunaitija")
            self.civilParishStr = readRow(row, "townshipseniunija")
            streets = readRow(row, "territorycoveredbyseniunaitija")
            self.municipalityStr = readRow(row, "municipality")
            self.uniqueKey = int(readRow(row, "uniquekeynotchangeable"))


            # skip empty entries
            if (self.seniunaitijaStr == ""):
                continue
            self.FixNames()


            # check that current Seniunaitija object does not already exist
            seniunaitija = Seniunaitija()
            seniunaitija.name = self.seniunaitijaStr
            seniunaitija.municipality = self.municipalityStr
            seniunaitija.civilParish = self.civilParishStr
            seniunaitija.id = self.uniqueKey

            print "saving Seniunaitija %s %s %s %s" % (seniunaitija.id,  seniunaitija.name, seniunaitija.civilParish, seniunaitija.municipality)

            seniunaitija.save()


            count += 1
            if (count >= maxNumberToImport):
                break

        print u"succesfully imported %d seniunaitija" % (count)