#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
from cdb_lt.management.commands.importSources import ltGeoDataSources_Institution
from contactdb.importUtils import readRow
import logging
from territories.houseNumberUtils import isHouseNumberOdd, yieldRanges, padHouseNumberWithZeroes
from territories.ltPrefixes import changeStreetFromShortToLongForm, allStreetEndings

logger = logging.getLogger(__name__)

city_genitive= u"Kauno miestas"
municipality= u"Kauno miesto savivaldybė"

class civilParishKaunasStreetReader(object):
    def __init__(self, civilParishFile=ltGeoDataSources_Institution.civilParishAddresses_Kaunas, delimiter=","):

        self.csvFileName = os.path.join(os.getcwd(), civilParishFile)
        self.delimiter = delimiter
        self.unparsedInstitutions = {}

    def currentTerritoryInfo(self):
        return "rowNumber  '%s' file'%s'" % (self.rowNumber, self.csvFileName)

    def yieldTerritories(self):
        reader = open(self.csvFileName, "rt")

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
        self.rowNumber = 0
        for row in lines:
            self.rowNumber += 1
            row = unicode(row, 'utf-8')
            id, civilParish, cityPart, streetCode, rest = row.split(" ", 4)

            # map id to civilParish
            civilParish = int(civilParish)
            civilParish = civilParishes[civilParish - 1]

            
            institutionKey= "%s %s" % (municipality, civilParish)

            # split into street and house numbers
            street = None
            for streetEnding in allStreetEndings:
                if rest.find(streetEnding) >= 0:
                    street, houseNumbers = rest.split(streetEnding)
                    # attach again street ending
                    street = "%s%s" % (street, streetEnding)
                    street = changeStreetFromShortToLongForm(street)
                    break
            if street is None:
                raise CivilParishNotFound("Could not split string '%s' into street and house number" % rest)

            # remove unwanted symbols
            houseNumbers = houseNumbers.replace(u"^", u"")
            # remove line ending symbol
            houseNumbers = houseNumbers[0:-1]
            # split by comma to have house numbers
            houseNumbers = houseNumbers.split(",")
            houseNumbers = [n.strip() for n in houseNumbers if (n != "")]

            for range in yieldRanges(houseNumbers):
                numberFrom = padHouseNumberWithZeroes(range.numberFrom)
                numberTo = padHouseNumberWithZeroes(range.numberTo)
                yield {"institutionKey" : institutionKey, "municipality" : municipality,
                           "civilParish" : civilParish, "city": city_genitive,
                           "street" : street, "numberFrom" : numberFrom,
                           "numberTo" : numberTo, "numberOdd": range.numberOdd,
                           "comment" : None}

