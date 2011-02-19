#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
from cdb_lt_civilparish.management.commands.importCivilParishStreets_Kaunas import yieldRanges, HouseRange
from cdb_lt_streets.searchInIndex import AddressDeducer
from contactdb.imp import ImportSources
from django.db import transaction
import csv
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_civilparish.models import CivilParish, CivilParishStreet
from pjutils.exc import ChainnedException
from cdb_lt_civilparish.management.commands.importCivilParish import readRow
from cdb_lt_streets.ltPrefixes import *
import logging
from cdb_lt_streets.houseNumberUtils import isStringStreetHouseNumber, StringIsNotAHouseNumberException, ifHouseNumberContainLetter, removeLetterFromHouseNumber, ContainsNumbers, ContainsHouseNumbers, padHouseNumberWithZeroes

logger = logging.getLogger(__name__)

civilParishFile = os.path.join(ltGeoDataSources.CivilParishIndexes_Vilnius, "vilniaus_miesto_seniunijos_visos.csv")

civilParishNames = [u"Antakalnio seniūnija",
    u"Fabijoniškių seniūnija",
    u"Justiniškių seniūnija",
    u"Karoliniškių seniūnija",
    u"Lazdynų seniūnija",
    u"Naujamiesčio seniūnija",
    u"Naujininkų seniūnija",
    u"Naujosios Vilnios seniūnija",
    u"Panerių seniūnija",
    u"Pašilaičių seniūnija",
    u"Pilaitės seniūnija",
    u"Rasų seniūnija",
    u"Senamiesčio seniūnija",
    u"Šeškinės seniūnija",
    u"Šnipiškių seniūnija",
    u"Verkių seniūnija",
    u"Vilkpėdės seniūnija",
    u"Viršuliškių seniūnija",
    u"Žirmūnų seniūnija",
    u"Žvėryno seniūnija"]

municipality= u"Vilniaus miesto savivaldybė"

class CivilParishNotFound(ChainnedException):
    pass

class ImportError(ChainnedException):
    pass

deducer = AddressDeducer()

class VilniusCivilParishReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = ImportSources.Delimiter)


    def readStreet(self):
        for row in self.dictReader:
            civilParishname = readRow(row, u"Seniunijos pav.")
            street = readRow(row, u"Gatves pavadinimas")
            house_numbers = readRow(row, u"Pastatu numeriai")
            city = readRow(row, u"miestas")

            yield civilParishname, city, street, house_numbers

class Command(BaseCommand):
    args = ''
    help = """Imports street data for CivilParish for city Vilnius"""

    def __init__(self):
        self.localCache = {}

    def getCivilParish(self, civilParishStr, municipality):
        key = "%s" % (civilParishStr)
        if self.localCache.has_key(key) == True:
            return self.localCache[key]

        try:
            civilParish = CivilParish.objects.all().filter(name = civilParishStr)\
                .filter(municipality__icontains = municipality)[0:1].get()
            self.localCache[key] = civilParish
            return civilParish
        except CivilParish.DoesNotExist:
            raise CivilParishNotFound(message = "Civil parish %s was not found" % civilParishStr)



    def create(self, civilParish = None, city = None, street = None, range = None):
        civilParishStreet = CivilParishStreet()
        civilParishStreet.street = street
        if range is not None:
            civilParishStreet.numberFrom = padHouseNumberWithZeroes(range.numberFrom)
            civilParishStreet.numberTo = padHouseNumberWithZeroes(range.numberTo)
            civilParishStreet.numberOdd = range.numberOdd
        civilParishStreet.city = city
        civilParishStreet.municipality = municipality
        civilParishStreet.institution = civilParish
        civilParishStreet.save()

    @transaction.commit_on_success
    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will import street data for CivilParish for city Vilnius:"

        logger.info("Will import Vilnius civil parish streets from following files")

        ImportSources.EsnureExists(civilParishFile)

        self.count = 0

        # fetch in one loop all civil parish objects,
        # zipped will contain file and civil parish object
        preFetchedCivilParishes = [self.getCivilParish(civilParishName, municipality) for civilParishName in civilParishNames]

        reader = VilniusCivilParishReader(civilParishFile)
        for civilParish, city, street, house_range in reader.readStreet():
            street = street.strip()
            street = changeStreetFromShortToLongForm(street)
            street = street.strip()
            print "%s %s %s %s" % (civilParish, city, street, house_range)
            if street == u"":
                #raise ImportError("street can not be null")
                continue

            civilParish = self.getCivilParish(civilParishStr=civilParish, municipality=municipality)
            for range in house_range.split(","):
                splittedRange = range.split("-")
                splittedRange = [p.strip() for p in splittedRange]
                r = None
                if len(splittedRange) == 1:
                    if splittedRange[0] != u"":
                        r = HouseRange(numberFrom=splittedRange[0])
                else:
                    r = HouseRange(numberFrom=splittedRange[0], numberTo=splittedRange[1])
                self.create(civilParish=civilParish, city=city, street=street, range=r)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

    """def insertAll(self, streetMap, civilParish):
        for street, houseNumbers in streetMap.iteritems():
            if street == u"V. Druskio gatvė":
                street = u"Virginijaus Druskio gatvė"

            #logger.debug("will import street %s" % street)
            for range in yieldRanges(houseNumbers):
                #logger.info("from: %s to %s  isOdd %s" % (range.numberFrom, range.numberTo, range.numberOdd))
                self.count += 1
                self.create(civilParish= civilParish, street = street, range= range)
                if self.count % 100 == 0:
                    logger.info("Inserted %s streets and counting" % self.count)
"""