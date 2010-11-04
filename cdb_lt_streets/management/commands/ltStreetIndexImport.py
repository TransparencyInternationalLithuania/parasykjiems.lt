#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import LithuanianStreetIndexes
from contactdb.imp import ImportSources
import csv
from pjutils.uniconsole import *
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from datetime import datetime

class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""
    def __init__(self):
        self.streetCache = {}
        self.initializeCache()
        pass

    def getCacheKey(self, municipality, city, street):
        return "%s %s %s" % (municipality, city, street)


    def addToCache(self, record):
        self.streetCache[self.getCacheKey(record.municipality, record.city, record.street)] = record

    def initializeCache(self):
        for r in LithuanianStreetIndexes.objects.all():
            self.addToCache(r)

    def isInCache(self, municipality, city, street):
        key = self.getCacheKey(municipality, city, street)
        return self.streetCache.has_key(key)

    def createIfNotNull(self, street, city, municipality):
        self.processedRecords += 1

        if (self.isInCache(municipality, city, street) == False):
            """try:

            LithuanianStreetIndexes.objects.all().filter(street = street) \
                .filter(city = city) \
                .filter(municipality = municipality) \
                [0:1].get()
            #print u"object %s %s %s exists, skipping" % (street, city, municipality)
        except LithuanianStreetIndexes.DoesNotExist:"""
            self.count += 1
            newObject = LithuanianStreetIndexes()
            newObject.street = street
            newObject.municipality = municipality
            newObject.city = city
            newObject.save()
            self.addToCache(newObject)

        seconds = (datetime.now() - self.start).seconds
        if (seconds - self.previousSecond > 1):
            self.previousSecond = seconds
            if (seconds == 0):
                rate = "unknown"
                rateProcessing = "unknown"
            else:
                rate = str(self.count / seconds)
                rateProcessing = str(self.processedRecords / seconds)
            print u"%s creating %s %s %s" % (self.count, street, city, municipality)
            print u"inserting at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, self.count)
            print u"processing at %s rows per second (total sec: %d, rows: %d)" % (rateProcessing, seconds, self.processedRecords)

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

            self.createIfNotNull(street, city, municipality)


    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will import lt street index data:"

        self.processedRecords = 0
        self.previousSecond = 0
        self.start = datetime.now()

        list = ltGeoDataSources.LithuanianStreetIndexes


        for doc, file in list:
            print "\t%s" % (file)
            ImportSources.EsnureExists(file, "ltGeoDataDownloadDocs")

        self.count = 0
        for doc, file in list:
            self.importFile(file)


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

