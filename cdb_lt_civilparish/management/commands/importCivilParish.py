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
from cdb_lt_municipality.models import MunicipalityMember, Municipality
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_civilparish.models import CivilParish
import logging

logger = logging.getLogger(__name__)

def readRow(row, key):
    key = key.lower()
    key = key.replace("_", "")
    if (row.has_key(key) == False):
        logger.debug("Could not find civil paris with key '%s'.  Will print now all possible keys:" % key)
        for p in row.iterkeys():
            logger.debug("key: '%s'" % p)
        row[key].strip()
    val = row[key]
    if (val is None):
        return u""
    return unicode(val.strip(), 'utf-8')


class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian CivilParish members / seniūnai'


    @transaction.commit_on_success
    def handle(self, *args, **options):
        fileName = ImportSources.LithuanianCivilParishes
        print u"Import civil parish data from csv file %s" % fileName
        ImportSources.EsnureExists(ImportSources.LithuanianCivilParishes)
        elapsedTime = TimeMeasurer()

        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = ImportSources.Delimiter)

        self.count = 0

        for row in self.dictReader:
            self.count += 1

            id = int(readRow(row, "id"))
            municipalityStr = readRow(row, "municipality")
            civilParishStr = readRow(row, "civilparish")

            if (civilParishStr == u""):
                continue

            civilParish = CivilParish()
            civilParish.id = id
            civilParish.name = civilParishStr
            civilParish.municipality = municipalityStr
            civilParish.save()


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count