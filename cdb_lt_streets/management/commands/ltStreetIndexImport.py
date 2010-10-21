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

class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""
    def __init__(self):
        pass


    def createIfNotNull(self, street, city, municipality):
        try:
            LithuanianStreetIndexes.objects.all().filter(street = street) \
                .filter(city = city) \
                .filter(municipality = municipality) \
                [0:1].get()
            print u"object %s %s %s exists, skipping" % (street, city, municipality)
        except LithuanianStreetIndexes.DoesNotExist:
            self.count += 1
            if (self.count % 1000 == 0):
                print u"%s creating %s %s %s" % (self.count, street, city, municipality)
            newObject = LithuanianStreetIndexes()
            newObject.street = street
            newObject.municipality = municipality
            newObject.city = city
            newObject.save()

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

        list = ltGeoDataSources.LithuanianStreetIndexes


        for doc, file in list:
            print "\t%s" % (file)
            ImportSources.EsnureExists(file, "ltGeoDataDownloadDocs")

        self.count = 0
        for doc, file in list:
            self.importFile(file)


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

