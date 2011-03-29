#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from cdb_lt.management.commands.createMembers import ImportSourcesMembers, makeSeniunaitijaInstitutionName
from contactdb.importUtils import readRow
from territories.houseNumberUtils import removeLetterFromHouseNumber, ContainsNumbers, padHouseNumberWithZeroes, isHouseNumberOdd
from pjutils.exc import ChainnedException
from territories.ltPrefixes import shortCityEndings, wholeCityEndings, shortStreetEndings, wholeStreetEndings, allStreetEndings, extractStreetEndingForm

import logging
logger = logging.getLogger(__name__)

class SeniunaitijaAddressExpanderException(ChainnedException):
    pass

class ExpandedStreet(object):
    """ The biggest house number that can possibly exist. This is usually used
    when in address range is refered in this form "from number 5 till the end".
    So the end in this case is this number"""
    MaxOddValue = 999999
    MaxEvenValue = 999999 - 1

    def __init__(self, street = None, numberFrom = None, numberTo = None, city = None):
        self.street = street
        if numberFrom is None:
            numberFrom = u""
        if numberTo is None:
            numberTo = u""
        self.numberFrom = numberFrom
        self.numberTo = numberTo
        self.city = city

class SeniunaitijaAddressExpander:
    zippedCityPrefixes = zip(shortCityEndings, wholeCityEndings)
    zippedStreetPrefixes = zip(shortStreetEndings, wholeStreetEndings)

    def GetCityPrefix(self, city, longPrefix):
        return "%s %s" % (city, longPrefix)

    def ContainsCity(self, street):
        for shortPrefix, longPrefix in self.zippedCityPrefixes:
            index = street.find(shortPrefix)
            if index >= 0:
                city = street[0:index].strip()
                city = self.GetCityPrefix(city, longPrefix)
                streetNew = street[index + len(shortPrefix):].strip()
                return (streetNew, city)
        return (None, None)



    def RemoveStreetParts(self, street):
        ending = extractStreetEndingForm(street)
        streetTuple = self._RemoveStreetPart(street, ending)

        """for ending in allStreetEndings:
            streetTuple = self._RemoveStreetPart(street, ending)
            if streetTuple is not None:
                break
"""
        """if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"skg.")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"g.")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"a.")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"pr.")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"pl.")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"al.")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"takas")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPart(street, u"alėja")"""
        if streetTuple is None:
            streetTuple = self._RemoveStreetPartSB(street, "SB")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPartSB(street, "sb")
        if streetTuple is None:
            streetTuple = self._RemoveStreetPartSB(street, "s/b")


        return streetTuple

    def _RemoveStreetPartSB(self, part, streetPartName):
        if part.find(streetPartName) >= 0:
            noName = part.split("Nr.")
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s" % (str)
            part = "%s %s" % (noName[-1], "Nr.")
            return (part, str)
        return None

    def _RemoveStreetPart(self, street, streetPartName):
        #if street.endswith(streetPartName):
        if streetPartName is None:
            return None
        if streetPartName == u"":
            return None
        if street.find(streetPartName) >= 0:
            noName = street.split(streetPartName)
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s %s" % (str, streetPartName)
            part = noName[-1]
            return (str, part)
        return None

    def ExpandStreetEnding(self, street):
        if street is None:
            return None
        if street == "":
            return ""
        #print "street %s" % street
        for shortPrefix, longPrefix in self.zippedStreetPrefixes:
            index = street.find(shortPrefix)
            if (index >= 0):
                expanded = "%s%s" % (street[0:index], longPrefix)
                return expanded
        return street

    def ExpandStreet(self, streets):
        """ yield a ExpandedStreet object for each house number found in street """

        if streets == "" or streets is None:
            yield ExpandedStreet()
            return

        if streets.strip() == "":
            yield ExpandedStreet()
            return

        if streets.find(u"išskyrus") >=0 :
            raise SeniunaitijaAddressExpanderException(u"territory contains 'except' / 'išskyrus' expressions. string '%s'" % streets)


        city = None
        lastStreet = None
        streetProperties = ""


        splitted = streets.split(u',')
        for street in splitted:
            numberTo = None
            numberFrom = None

            street = street.strip()

            # separate city from street
            streetNew, cityNew = self.ContainsCity(street)
            if cityNew is not None:
                street, city  = streetNew, cityNew

            # separate street number from street
            streetTuple = self.RemoveStreetParts(street)

            # if no street prefix found, then whole street is actually a street number,
            # if it contains numbers. if it does not contain numbers, treat it as city name
            if streetTuple is not None:
                street, streetProperties = streetTuple
            else:
                if street != u"":
                    if ContainsNumbers(street) == True:
                        streetProperties = street
                        street = lastStreet
                    else:
                        city = street
                        streetProperties = None
                        street = None
                else:
                    street = None

            # expand street
            street = self.ExpandStreetEnding(street)

            # parse street number
            if streetProperties == u"" or streetProperties is None:
                numberFrom = None
            else:
                oldProp = streetProperties
                odd = None
                if streetProperties.find(u"neporiniai") >= 0:
                    odd = 1
                elif streetProperties.find(u"poriniai") >= 0:
                    odd = 0
                streetProperties = streetProperties.lower()

                streetProperties = streetProperties.replace(u"neporiniai", u"") \
                    .replace(u"poriniai", u"").replace(u"nuo", u"") \
                    .replace(u"nr.:", u"") \
                    .replace(u"nr.", u"")\
                    .replace(u"nr", u"") \
                    .replace(u"numeriai", u"") \
                    .replace(u"individualiųjų namų dalis", u"").replace(u"namo", u"") \
                    .replace(u"namai", u"") \
                    .replace(u"gyv. namai", u"").replace(u"gyv. namas", u"") \
                    .replace(u"(", u"").replace(u")", u"").strip()
                #print streetProperties
                # the numbers will contain ranges

                if self.ContainsRanges(streetProperties):
                #if (streetProperties.find("iki") >= 0):
                    # sometimes we might have more than one range
                    # so split it into individual
                    for numberFrom, numberTo in self.SplitToRanges(streetProperties):
                        numberFrom = numberFrom.strip()
                        numberTo = numberTo.strip()
                        try:
                            numberFrom = removeLetterFromHouseNumber(numberFrom)
                            numberFrom = int(numberFrom)
                        except:
                            raise SeniunaitijaAddressExpanderException("could not convert string '%s' to number" % numberFrom)

                        try:
                            if numberTo == u"galo":
                                isOdd = numberFrom % 2
                                if isOdd == 0:
                                    numberTo = ExpandedStreet.MaxEvenValue
                                else:
                                    numberTo = ExpandedStreet.MaxOddValue
                            else:
                                numberTo = removeLetterFromHouseNumber(numberTo)
                                numberTo = int(numberTo)
                        except:
                            raise SeniunaitijaAddressExpanderException("could not convert string '%s' to number" % numberTo)

                        yield ExpandedStreet(street = street, city = city, numberFrom = numberFrom, numberTo = numberTo)
                    # we have yielded already, continue
                    lastStreet = street
                    continue

                else:
                    # else it will be simple number
                    if not ContainsNumbers(streetProperties):
                        raise SeniunaitijaAddressExpanderException("string '%s' does not contain numbers. Though i expected it to be a house number" % streetProperties)

                    streetProperties = removeLetterFromHouseNumber(streetProperties)
                    #print streetProperties
                    try:
                        numberFrom = int(streetProperties)
                    except:
                        raise SeniunaitijaAddressExpanderException("could not convert string '%s' to number" % streetProperties)

            lastStreet = street

            yield ExpandedStreet(street = street, city = city, numberFrom = numberFrom, numberTo = numberTo)

    def SplitToRanges(self, streetProperties):
        for s1 in streetProperties.split("ir"):
            for s in s1.split(u";"):
                if s.find("iki") >=0:
                    r = s.split("iki")
                    if len(r) != 2:
                        raise SeniunaitijaAddressExpanderException("string '%s' had more than 1 range" % s)
                    yield r
                elif s.find(u"-") >= 0:
                    r = s.split("-")
                    if len(r) != 2:
                        raise SeniunaitijaAddressExpanderException("string '%s' had more than 1 range" % s)
                    yield r
                elif s.find(u"–") >= 0:
                    r = s.split(u"–")
                    if len(r) != 2:
                        raise SeniunaitijaAddressExpanderException("string '%s' had more than 1 range" % s)
                    yield r

                else:
                    raise SeniunaitijaAddressExpanderException("string '%s' did not contain any ranges. Whole string '%s'" % (s, streetProperties))



    def ContainsRanges(self, streetProperties):
        if streetProperties.find(u"iki") >=0:
            return True

        if streetProperties.find(u"–") >= 0:
            return True

        if streetProperties.find(u"-") >=0:
            return True

        return False

class seniunaitijaStreetReader(object):
    def __init__(self, fileName = ImportSourcesMembers.LithuanianSeniunaitijaMembers, institutionNameGetter= makeSeniunaitijaInstitutionName, delimieter=","):
        self.fileName = fileName
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter=delimieter)
        self.institutionNameGetter = institutionNameGetter
        self.unparsedInstitutions = {}


    def currentTerritoryInfo(self):
        return "rowNumber  '%s' file'%s'" % (self.processedCount, self.fileName)

    def yieldTerritories(self):
        emptyTerritoryCount = 0
        self.processedCount = 0
        streetExpander = SeniunaitijaAddressExpander()
        wasError = 0



        for row in self.dictReader:
            self.processedCount += 1
            territoryStr = readRow(row, "territorycoveredbyseniunaitija")
            municipality = readRow(row, "municipality")
            uniquekey = readRow(row, "uniquekey")
            seniunaitijaName = readRow(row, "seniunaitija")
            civilParish = readRow(row, "civilparish")
            institutionKey = self.institutionNameGetter(row)

            if territoryStr == u"":
                emptyTerritoryCount += 1
                continue

            if seniunaitijaName == u"":
                logger.info("skipping teritory %s" % self.processedCount)
                continue

            numberOfStreets = 0
            if self.processedCount % 100 == 0:
                logger.info("territory for: %s %s" % (self.processedCount, seniunaitijaName))



            try:
                for expandedStreet in streetExpander.ExpandStreet(territoryStr):
                    numberOfStreets += 1

                    city = expandedStreet.city
                    if city is None:
                        city = u""
                    street = expandedStreet.street
                    if street is None:
                        street = u""
                    numberFrom = padHouseNumberWithZeroes(expandedStreet.numberFrom)
                    if numberFrom is not None:
                        numberOdd = isHouseNumberOdd(expandedStreet.numberFrom)
                    numberTo = padHouseNumberWithZeroes(expandedStreet.numberTo)
                    yield (institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
            except SeniunaitijaAddressExpanderException as e:
                self.unparsedInstitutions[institutionKey] = "Could not parse territory for seniunaitija '%s' uniquekey '%s'. Error message:%s " % (seniunaitijaName, uniquekey, e.message)
                wasError += 1
                continue