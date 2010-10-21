#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from contactdb.imp import ImportSources
from django.db import transaction
import csv
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_civilparish.models import CivilParish, CivilParishStreet
from pjutils.exc import ChainnedException

class CivilParishNotFound(ChainnedException):
    pass

class Command(BaseCommand):
    args = ''
    help = """"""

    def __init__(self):
        self.localCache = {}

    def getCivilParish(self, civilParishStr):
        key = "%s" % (civilParishStr)
        if (self.localCache.has_key(key) == True):
            return self.localCache[key]

        try:
            civilParish = CivilParish.objects.all().filter(name = civilParishStr)[0:1].get()
            self.localCache[key] = civilParish
            return civilParish
        except CivilParish.DoesNotExist:
            raise CivilParishNotFound(message = "Civil parish %s was not found" % civilParishStr)



    def createIfNotNull(self, street, city, municipality, civilParishStr):
        civilParish = self.getCivilParish(civilParishStr)

        civilParishStreet = CivilParishStreet()
        civilParishStreet.street = street
        civilParishStreet.city = city
        civilParishStreet.municipality = municipality
        civilParishStreet.civilParish = civilParish
        civilParishStreet.save()
        self.count += 1


    @transaction.commit_on_success
    def importFile(self, fileName):
        print u"Import street index data from csv file %s" % fileName

        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")

        for row in self.dictReader:
            id = unicode(row["id"].strip(), 'utf-8')
            country = unicode(row["country"].strip(), 'utf-8')
            county = unicode(row["county"].strip(), 'utf-8')
            municipality = unicode(row["municipality"].strip(), 'utf-8')
            civilParish = unicode(row["civilparish"].strip(), 'utf-8')
            city = unicode(row["city"].strip(), 'utf-8')
            street = unicode(row["street"].strip(), 'utf-8')

            if (civilParish == u""):
                continue

            self.createIfNotNull(street, city, municipality, civilParish)



    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will import lt civil parish street index data:"

        list = ltGeoDataSources.CivilParishIndexes


        for doc, file in list:
            print "\t%s" % (file)
            ImportSources.EsnureExists(file)

        self.count = 0
        for doc, file in list:
            self.importFile(file)


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

