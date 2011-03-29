#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import HierarchicalGeoData
import csv
from pjutils.uniconsole import *

class Command(BaseCommand):
    args = '<>'
    help = """Imports data from csv files into HierarchicalGeoData table. This is only used to scan register center web page"""
    def __init__(self):
        self.localCache = {}


    def createIfNotNull(self, name, type, parent = None):
        key = "%s%s" % (name, type)
        if (parent is not None):
            key = "%s%s%s" % (name, type, parent.id)

        if (self.localCache.has_key(key) == True):
            return self.localCache[key]

        try:

            existing = HierarchicalGeoData.objects.all().filter(name = name) \
                .filter(type = type)
            if (parent is None):
                existing = existing.filter(parent__isnull = True)
            else:
                existing = existing.filter(parent = parent)
            existing = existing[0:1].get()
            self.localCache[key] = existing
            print u"object %s %s exists, skipping" % (name, type)
            return existing
        except HierarchicalGeoData.DoesNotExist:
            self.count += 1
            if (self.count % 1000 == 0):
                print u"%s creating %s %s" % (self.count, name, type)
            newObject = HierarchicalGeoData(name = name, type = type, parent = parent)
            newObject.save()
            self.localCache[key] = newObject
            return newObject

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

            parent = self.createIfNotNull(country, HierarchicalGeoData.HierarchicalGeoDataType.Country)
            parent = self.createIfNotNull(county, HierarchicalGeoData.HierarchicalGeoDataType.County, parent = parent)
            parent = self.createIfNotNull(municipality, HierarchicalGeoData.HierarchicalGeoDataType.Municipality, parent = parent)
            parent = self.createIfNotNull(civilParish, HierarchicalGeoData.HierarchicalGeoDataType.CivilParish, parent = parent)
            parent = self.createIfNotNull(city, HierarchicalGeoData.HierarchicalGeoDataType.City, parent = parent)
            parent = self.createIfNotNull(street, HierarchicalGeoData.HierarchicalGeoDataType.Street, parent = parent)


    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will import lt street index data:"

        list = ltGeoDataSources.LithuanianStreetIndexes


        for doc, file in list:
            print "\t%s" % (file)
            ImportSources.EsnureExists(file)

        self.count = 0
        for doc, file in list:
            self.importFile(file)


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

