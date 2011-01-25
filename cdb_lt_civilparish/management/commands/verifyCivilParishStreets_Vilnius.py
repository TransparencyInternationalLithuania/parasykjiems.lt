#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
from cdb_lt_civilparish.management.commands.importCivilParishStreets_Kaunas import yieldRanges
from contactdb.imp import ImportSources
from django.db import transaction
from cdb_lt_civilparish.management.commands.importCivilParishStreets_Vilnius  import zippedVilniusCivilParishes, getCivilParishStreetMap
from pjutils.timemeasurement import TimeMeasurer
import logging

logger = logging.getLogger(__name__)

def searchSimilarStreets(civilParishStreetMaps):

    allStreets = {}
    for civilParish, civilParishStreets in civilParishStreetMaps.iteritems():
        for street, streetRanges in civilParishStreets.iteritems():
            if not allStreets.has_key(street):
                allStreets[street] = {}
            allStreets[street][civilParish] = streetRanges

    invalidStreetCount = 0
    for street, streetRanges in allStreets.iteritems():
        if len(list(streetRanges.iterkeys())) < 2:
            continue
        # test if we have similar ranges
        count = 0
        for civilparish, streetRange in list(streetRanges.iteritems())[0:-1]:
            count += 1
            streetsAreEqual = True
            for civilParish_test, streetRange_test in list(streetRanges.iteritems())[count:]:
                if not len(streetRange_test) == len(streetRange):
                    streetsAreEqual = False

        if streetsAreEqual == False:
            continue
        print "\n"
        print "street %s is also included in these civil parishes: " % street
        invalidStreetCount += 1
        for c in streetRanges.iterkeys():
            print c
    print "\n total invalid street count: %s" % invalidStreetCount

"""
    for key, civilParishStreets in civilParishStreetMaps.iteritems():
        print "Searching for similar streets for civil parish %s" % key

        for key_test, civilParishStreets_test in civilParishStreetMaps.iteritems():
            if key == key_test:
                continue
            for test_street, test_street_ranges in civilParishStreets_test.iteritems():
                if not civilParishStreets.has_key(test_street):
                    continue
                real_streets = civilParishStreets[test_street]
                if not len(test_street_ranges) == len(real_streets):
                    continue
                
                print "Similar street %s \t %s" % (test_street, key_test)
                """


class Command(BaseCommand):
    args = ''
    help = """Imports street data for CivilParish for city Vilnius"""

    def __init__(self):
        pass

    @transaction.commit_on_success
    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will test street data for CivilParish for city Vilnius:"

        logger.info("Will test Vilnius civil parish streets from following files")
        for file, name in zippedVilniusCivilParishes:
            logger.info("name: %s" % (name))
            logger.info("file: %s \n" % (file))
            ImportSources.EsnureExists(file)

        self.count = 0


        civilParishStreetMaps = {}

        # read each file one by one, and insert streets
        for file, civilParish in zippedVilniusCivilParishes:
            logger.info("\n parsing file %s \n" %  file)
            civilParishStreetMaps[civilParish] = getCivilParishStreetMap(file)

        # search for similar streets
        searchSimilarStreets(civilParishStreetMaps)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count