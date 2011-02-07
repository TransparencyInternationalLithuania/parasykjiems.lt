#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
from cdb_lt_civilparish.management.commands.importCivilParishStreets_Kaunas import yieldRanges
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
from cdb_lt_streets.houseNumberUtils import isStringStreetHouseNumber, StringIsNotAHouseNumberException, ifHouseNumberContainLetter, removeLetterFromHouseNumber, ContainsNumbers, ContainsHouseNumbers

logger = logging.getLogger(__name__)

civilParishFiles = [u"antakalnis.csv",
            u"fabijoniskes.csv",
            u"justiniskes.csv",
            u"karoliniskes.csv",
            u"lazdynai.csv",
            u"naujamiestis.csv",
            u"naujininkai.csv",
            u"naujoji_vilnia.csv",
            u"paneriai.csv",
            u"pasilaiciai.csv",
            u"pilaite.csv",
            u"rasos.csv",
            u"senamiestis.csv",
            u"seskine.csv",
            u"snipiskes.csv",
            u"verkiai.csv",
            u"vilkpede.csv",
            u"virsuliskes.csv",
            u"zirmunai.csv",
            u"zverynas.csv"]

civilParishFiles = [os.path.join(ltGeoDataSources.CivilParishIndexes_Vilnius, p) for p in civilParishFiles]

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

zippedVilniusCivilParishes = zip(civilParishFiles, civilParishNames)

class CouldNotSpleetIntoStreetAndHouseNumber(ChainnedException):
    pass




def splitIntoStreetAndHouseNumbers(string):
    # split into street and house numbers
    street = None
    houseNumber = None
    endings = allStreetEndings + [u"krantinė"]
    for streetEnding in endings:
        if string.find(streetEnding) >= 0:
            street, houseNumber = string.split(streetEnding)
            # attach again street ending
            street = "%s%s" % (street, streetEnding)
            street = changeStreetFromShortToLongForm(street)
            break
    if street is None:
        raise CouldNotSpleetIntoStreetAndHouseNumber("Could not split string '%s' into street and house number" % rest)
    return street, houseNumber

city = u"Vilnius"
city_genitive= u"Vilniaus miestas"
municipality= u"Vilniaus miesto savivaldybė"


def extractStreetsAndHouseNumbers(fileName):
    """ Will read one of files in Vilnius Civil Parish street, and will return street and numbers"""
    reader = open(fileName, "rt")
    lines = reader.readlines()


    currentStreet = None
    state = u"ReadStreetName"
    for row in lines:
        row = unicode(row, 'utf-8')
        row = row.strip()

        #logger.info("parsing row: '%s'" % row)

        # skip empty lines
        if row == u"":
            continue

        # first line is street name, second is house numbers
        if state == u"ReadStreetName":
            # first line can sometimes contain two streets, so handle this case
            # P.s. some streets, such as "Sausio 13-osios g.", contains number in the middle
            # This case ideally should be handheld with regexp, but for now just use single - if to filter this out
            if ContainsHouseNumbers(row) and row.find(u"13-osios") < 0:
                # split into two streets, and yield first street with house number
                firstStreet, secondStreet = row.split(u",")
                streetName, houseNumber = splitIntoStreetAndHouseNumbers(firstStreet)
                houseNumber = houseNumber.strip()
                yield (streetName, houseNumber)

                # store second street for later loop
                currentStreet = secondStreet
                currentStreet = changeStreetFromShortToLongForm(currentStreet)
            else:
                # store second street for later loop
                currentStreet = row
                currentStreet = changeStreetFromShortToLongForm(currentStreet)
            state = u"ReadHouseNumbers"
        else:
            # extract house numbers, and yield with current street
            houseNumbers = row.split(",")
            for number in houseNumbers:
                if (number.find(u"_") >=0):
                    number = number.split(u"_")[0]
                number = number.strip()
                if number == u"":
                    continue
                yield (currentStreet, number)

            # change state back to read street name
            state = u"ReadStreetName"

def getCivilParishStreetMap(file):
    """ Given a vilnius city street index file,
    will read it, and create a dictionary where key is street name,
    and value is a list of all house numbers in that street"""
    streetMap = {}
    # first collect all streets, and their house numbers
    # since these are scattered throughout the files
    for street, houseNumber in extractStreetsAndHouseNumbers(file):
        list = streetMap.get(street, [])
        list.append(houseNumber)
        streetMap[street] = list
    return streetMap

class CivilParishNotFound(ChainnedException):
    pass

class Command(BaseCommand):
    args = ''
    help = """Imports street data for CivilParish for city Vilnius"""

    def __init__(self):
        self.localCache = {}

    def getCivilParish(self, civilParishStr, municipality):
        key = "%s" % (civilParishStr)
        if (self.localCache.has_key(key) == True):
            return self.localCache[key]

        try:
            civilParish = CivilParish.objects.all().filter(name = civilParishStr)\
                .filter(municipality__icontains = municipality)[0:1].get()
            self.localCache[key] = civilParish
            return civilParish
        except CivilParish.DoesNotExist:
            raise CivilParishNotFound(message = "Civil parish %s was not found" % civilParishStr)



    def create(self, civilParish = None, street = None, range = None):
        civilParishStreet = CivilParishStreet()
        civilParishStreet.street = street
        civilParishStreet.city = city
        civilParishStreet.numberFrom = range.numberFrom
        civilParishStreet.numberTo = range.numberTo
        civilParishStreet.numberOdd = range.numberOdd
        civilParishStreet.city_genitive = city_genitive
        civilParishStreet.municipality = municipality
        civilParishStreet.institution = civilParish
        civilParishStreet.save()

    @transaction.commit_on_success
    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will import street data for CivilParish for city Vilnius:"

        logger.info("Will import Vilnius civil parish streets from following files")
        for file, name in zippedVilniusCivilParishes:
            logger.info("name: %s" % (name))
            logger.info("file: %s \n" % (file))
            ImportSources.EsnureExists(file)

        self.count = 0

        # fetch in one loop all civil parish objects,
        # zipped will contain file and civil parish object
        zipped = [(file, self.getCivilParish(civilParishName, municipality)) for file, civilParishName in zippedVilniusCivilParishes]

        # read each file one by one, and insert streets
        for file, civilParish in zipped:
            logger.info("\n parsing file %s \n" %  file)

            civilParishStreetMap = getCivilParishStreetMap(file)
            # now loop again, construct house ranges from house numbers, and insert
            self.insertAll(civilParishStreetMap, civilParish= civilParish)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

    def insertAll(self, streetMap, civilParish):
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
