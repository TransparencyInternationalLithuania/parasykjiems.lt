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
from cdb_lt_civilparish.management.commands.importCivilParish import readRow
from cdb_lt_streets.ltPrefixes import *
import logging
from cdb_lt_streets.houseNumberUtils import isStringStreetHouseNumber, StringIsNotAHouseNumberException, ifHouseNumberContainLetter, removeLetterFromHouseNumber

logger = logging.getLogger(__name__)

class CivilParishNotFound(ChainnedException):
    pass

class HouseRange:
    def __init__(self, numberFrom = None, numberTo = None, numberOdd = None):
        self.numberFrom = numberFrom
        self.numberTo = numberTo
        if (numberTo is None):
            numberFrom = removeLetterFromHouseNumber(numberFrom)
            self.numberOdd = int(numberFrom) % 2 == 1
        else:
            self.numberOdd = numberOdd

def _collectRanges(numberList):
    if (len(numberList) == 0):
        return 
    first = numberList[0]
    last = first
    for next in numberList[1:]:
        if last + 2 == next:
            last = next
            continue

        # yield current number
        if (first == last):
            yield HouseRange(str(first))
        else:
            yield HouseRange(str(first), str(last), first % 2 == 1)
        first = next
        last = next

    if (first == last):
        yield HouseRange(str(first))
    else:
        yield HouseRange(str(first), str(last), first % 2 == 1)

def yieldRanges(listOfHouseNumbers):
    oddNumbers = []
    evenNumbers = []

    # Divide house numbers into even and odd
    # spit out house numbers with letters immediatelly
    for num in listOfHouseNumbers:
        if (num is None):
            continue
        if (num == ""):
            continue
        if isStringStreetHouseNumber(num) == False:
            raise StringIsNotAHouseNumberException(message="string '%s' is not a house number " % num)
        if ifHouseNumberContainLetter(num):
            yield HouseRange(num)
            continue
        num = int(num)
        isOdd = (num % 2) == 1
        if isOdd:
            oddNumbers.append(num)
        else:
            evenNumbers.append(num)


    for range in _collectRanges(oddNumbers):
        yield range

    for range in _collectRanges(evenNumbers):
        yield range
            

class Command(BaseCommand):
    args = ''
    help = """Imports street data for CivilParish for city Kaunas"""

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



    def create(self, civilParish = None, street = None, range = None):
        city = u"Kaunas"
        city_genitive= u"Kauno miestas"
        municipality= u"Kauno miesto savivaldybė"
        
        civilParishStreet = CivilParishStreet()
        civilParishStreet.street = street
        civilParishStreet.city = city
        civilParishStreet.numberFrom = range.numberFrom
        civilParishStreet.numberTo = range.numberTo
        civilParishStreet.numberOdd = range.numberOdd
        civilParishStreet.city_genitive = city_genitive
        civilParishStreet.municipality = municipality
        civilParishStreet.civilParish = civilParish
        civilParishStreet.save()
        

    @transaction.commit_on_success
    def importFile(self, fileName):
        reader = open(fileName, "rt")

        civilParishes = [u"Centro seniūnija",
            u"Žaliakalnio seniūnija",
            u"Šančių seniūnija",
            u"Dainavos seniūnija",
            u"Gričiupio seniūnija",
            u"Petrašiūnų seniūnija",
            u"Panemunės seniūnija",
            u"Aleksoto seniūnija",
            u"Eigulių seniūnija",
            u"Vilijampolės seniūnija",
            u"Šilainių seniūnija"]



        lines = reader.readlines()
        for row in lines:
            row = unicode(row, 'utf-8')
            id, civilParish, cityPart, streetCode, rest = row.split(" ", 4)
            
            # map id to civilParish
            civilParish = int(civilParish)
            civilParish = civilParishes[civilParish - 1]
            # map string to civil parish object
            civilParish = self.getCivilParish(civilParish)

            # split into street and house numbers
            street = None
            endings = allStreetEndings + [u"krantinė"]
            for streetEnding in endings:
                if (rest.find(streetEnding) >= 0):
                    street, houseNumbers = rest.split(streetEnding)
                    # attach again street ending
                    street = "%s%s" % (street, streetEnding)
                    street = changeStreetFromShortToLongForm(street)
                    break
            if (street is None):
                raise CivilParishNotFound("Could not split string '%s' into street and house number" % rest) 

            # remove unwanted symbols
            houseNumbers = houseNumbers.replace(u"^", u"")
            # remove line ending symbol
            houseNumbers = houseNumbers[0:-1]
            # split by comma to have house numbers
            houseNumbers = houseNumbers.split(",")
            houseNumbers = [n.strip() for n in houseNumbers if (n != "")]

            #print "\n \n"
            #print "row: %s" % row

            for range in yieldRanges(houseNumbers):
                #print "from: %s to %s  isOdd %s" % (range.numberFrom, range.numberTo, range.numberOdd)
                self.count += 1
                self.create(civilParish= civilParish, street = street, range= range)
                if self.count % 100 == 0:
                    logger.info("Inserted %s streets and counting" % self.count)
            """

            self.createIfNotNull(street, city, municipality, civilParish, city_genitive=city_genitive)
"""

    def handle(self, *args, **options):
        elapsedTime = TimeMeasurer()
        print "Will import street data for CivilParish for city Kaunas:"

        self.count = 0
        list = ltGeoDataSources.CivilParishIndexes

        ImportSources.EsnureExists(ltGeoDataSources.CivilParishIndexes_Kaunas)

        self.importFile(ltGeoDataSources.CivilParishIndexes_Kaunas)


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count

