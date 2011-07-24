#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
from cdb_lt.management.commands.importSources import ltGeoDataSources_Institution
from contactdb.importUtils import readRow
import logging
from territories.houseNumberUtils import HouseRange, padHouseNumberWithZeroes
from territories.ltPrefixes import changeStreetFromShortToLongForm

logger = logging.getLogger(__name__)

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

class VilniusCivilParishReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = ",")


    def readStreet(self):
        for row in self.dictReader:
            civilParishname = readRow(row, u"Seniunijos pav.")
            street = readRow(row, u"Gatves pavadinimas")
            house_numbers = readRow(row, u"Pastatu numeriai")
            city = readRow(row, u"miestas")

            yield civilParishname, city, street, house_numbers

class civilParishVilniusStreetReader(object):
    def __init__(self, civilParishFile=ltGeoDataSources_Institution.civilParishAddresses_Vilnius, delimiter=","):

        self.csvFileName = os.path.join(os.getcwd(), civilParishFile)
        self.delimiter = delimiter
        self.unparsedInstitutions = {}

    def currentTerritoryInfo(self):
        return "rowNumber  '%s' file'%s'" % (self.rowNumber, self.csvFileName)


    def yieldTerritories(self):
        reader = VilniusCivilParishReader(self.csvFileName)
        self.rowNumber = 0

        for civilParish, city, street, house_range in reader.readStreet():
            self.rowNumber += 1
            street = street.strip()
            street = changeStreetFromShortToLongForm(street)
            street = street.strip()
            if street == u"":
                continue

            for range in house_range.split(","):
                splittedRange = range.split("-")
                splittedRange = [p.strip() for p in splittedRange]
                r = HouseRange()
                if len(splittedRange) == 1:
                    if splittedRange[0] != u"":
                        r = HouseRange(numberFrom=splittedRange[0])
                else:
                    r = HouseRange(numberFrom=splittedRange[0], numberTo=splittedRange[1])
                institutionKey= "%s %s" % (municipality, civilParish)

                numberFrom = padHouseNumberWithZeroes(r.numberFrom)
                numberTo = padHouseNumberWithZeroes(r.numberTo)
                yield {"institutionKey" : institutionKey, "municipality" : municipality,
                           "civilParish" : civilParish, "city": city,
                           "street" : street, "numberFrom" : numberFrom,
                           "numberTo" : numberTo, "numberOdd": r.numberOdd,
                           "comment" : None}

