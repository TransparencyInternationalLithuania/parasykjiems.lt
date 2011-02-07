#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from django.db import connection, transaction
from pjutils.timemeasurement import TimeMeasurer
import pjutils.uniconsole
import os
from pjutils.exc import ChainnedException
import logging
import re
from cdb_lt_seniunaitija.models import SeniunaitijaStreet, Seniunaitija
from contactdb.imp import ImportSources
from cdb_lt_seniunaitija.management.commands.importSeniunaitijaMembers import SeniunaitijaMembersReader
from cdb_lt_mps.models import PollingDistrictStreet
from cdb_lt_streets.searchInIndex import *
from cdb_lt_streets.houseNumberUtils import removeLetterFromHouseNumber, ContainsNumbers

logger = logging.getLogger(__name__)

class ExpandedStreet(object):
    """ The biggest house number that can possibly exist. This is usually used
    when in address range is refered in this form "from number 5 till the end".
    So the end in this case is this number"""
    MaxOddValue = 999999
    MaxEvenValue = 999999 - 1

    def __init__(self, street = None, numberFrom = None, numberTo = None, city = None):
        self.street = street
        self.numberFrom = numberFrom
        self.numberTo = numberTo
        self.city = city

class SeniunaitijaAddressExpanderException(ChainnedException):
    pass

class SeniunaitijaAddressExpander:
    zippedCityPrefixes = zip(shortCityEndings, wholeCityEndings)
    zippedStreetPrefixes = zip(shortStreetEndings, wholeStreetEndings)

    def GetCityPrefix(self, city, longPrefix):
        return "%s %s" % (city, longPrefix)

    def ContainsCity(self, street):
        for shortPrefix, longPrefix in self.zippedCityPrefixes:
            index = street.find(shortPrefix)
            if (index >= 0):
                city = street[0:index].strip()
                city = self.GetCityPrefix(city, longPrefix)
                streetNew = street[index + len(shortPrefix):].strip()
                return (streetNew, city)
        return (None, None)



    def RemoveStreetParts(self, street):
        streetTuple = None
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"skg.")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"g.")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"a.")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"pr.")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"pl.")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"al.")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"takas")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPart(street, u"alėja")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPartSB(street, "SB")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPartSB(street, "sb")
        if (streetTuple is None):
            streetTuple = self._RemoveStreetPartSB(street, "s/b")


        return streetTuple

    def _RemoveStreetPartSB(self, part, streetPartName):
        if (part.find(streetPartName) >= 0):
            noName = part.split("Nr.")
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s" % (str)
            part = "%s %s" % (noName[-1], "Nr.")
            return (part, str)
        return None

    def _RemoveStreetPart(self, street, streetPartName):
        if (street.find(streetPartName) >= 0):
            noName = street.split(streetPartName)
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s %s" % (str, streetPartName)
            part = noName[-1]
            return (str, part)
        return None

    def ExpandStreetEnding(self, street):
        if (street is None):
            return None
        if (street == ""):
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

        if (streets == "" or streets is None):
            yield ExpandedStreet()
            return

        if (streets.strip() == ""):
            yield ExpandedStreet()
            return

        if (streets.find(u"išskyrus") >=0 ):
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
            if (cityNew is not None):
                street, city  = streetNew, cityNew

            # separate street number from street
            streetTuple = self.RemoveStreetParts(street)

            # if no street prefix found, then whole street is actually a street number,
            # if it contains numbers. if it does not contain numbers, treat it as city name
            if (streetTuple is not None):
                street, streetProperties = streetTuple
            else:
                if (street != u""):
                    if (ContainsNumbers(street) == True):
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
            if (streetProperties == u"" or streetProperties is None):
                numberFrom = None
            else:
                oldProp = streetProperties
                odd = None
                if (streetProperties.find(u"neporiniai") >= 0):
                    odd = 1
                elif (streetProperties.find(u"poriniai") >= 0):
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

                if (self.ContainsRanges(streetProperties)):
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
                            if (numberTo == u"galo"):
                                isOdd = numberFrom % 2
                                if (isOdd == 0):
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
                    if (ContainsNumbers(streetProperties) == False):
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
                    if (len(r) != 2):
                        raise SeniunaitijaAddressExpanderException("string '%s' had more than 1 range" % s)
                    yield r
                elif (s.find(u"-") >= 0):
                    r = s.split("-")
                    if (len(r) != 2):
                        raise SeniunaitijaAddressExpanderException("string '%s' had more than 1 range" % s)
                    yield r
                elif (s.find(u"–") >= 0):
                    r = s.split(u"–")
                    if (len(r) != 2):
                        raise SeniunaitijaAddressExpanderException("string '%s' had more than 1 range" % s)
                    yield r

                else:
                    raise SeniunaitijaAddressExpanderException("string '%s' did not contain any ranges. Whole string '%s'" % (s, streetProperties))



    def ContainsRanges(self, streetProperties):
        if streetProperties.find(u"iki") >=0:
            return True

        if (streetProperties.find(u"–") >= 0):
            return True

        if streetProperties.find(u"-") >=0:
            return True

        return False


class Command(BaseCommand):
    args = '<>'
    help = """ """

    previousDBRowCount = None

    def getPollingDistricts(self, aggregator, fromPrint, toPrint):
        count = 0

        pollingDistricts = []

        for pollingDistrict in aggregator.getLocations():
            if (count + 1 > toPrint):
                break
            count += 1
            if (count + 1 <= fromPrint):
                continue
            pollingDistricts.append(pollingDistrict)
        return pollingDistricts



    def preFetchAllConstituencies(self, pollingDistricts):
        time = TimeMeasurer()
        # fetch all counties in pseudo batch,
        constituencies = {}

        for pol in pollingDistricts:
            if (constituencies.has_key(pol.Constituency.nr) == False):
                try:
                    constituencies[pol.Constituency.nr] = Constituency.objects.get(nr = pol.Constituency.nr)
                except Constituency.DoesNotExist as e:
                    raise ImportStreetsConstituencyDoesNotExist("constituency '%s' was not found in DB. Maybe you forgot to import them : manage.py importConstituencies?  Or else it might not exist in source data, in which case you will have to resolve manually this issue", e)


            constituency = constituencies[pol.Constituency.nr]
            # re-assign old constituency to new constituency fetched from database
            pol.Constituency = constituency
        print u"finished pre-fetching. Took %s seconds" % time.ElapsedSeconds()

    def RemoveExistingStreets(self, expandedStreets, street, pollingDistrict):
        nonExisting = []

        # a minor optimization hack, to improve speed when inserting data first time

        # check how many rows we have initially
        if (self.previousDBRowCount is None):
            self.previousDBRowCount = PollingDistrictStreet.objects.count()

        # if we have none rows, then just return list, and do any checks,
        # no need to do that, right
        if (self.previousDBRowCount == 0):
            return expandedStreets

        # will execute looots of selectes against database
        # it will be veerry slow, but works for now
        for expandedStreet in expandedStreets:
            query = PollingDistrictStreet.objects.filter(constituency = pollingDistrict.Constituency)
            query = query.filter(district = pollingDistrict.District)
            query = query.filter(city = street.cityName)
            query = query.filter(street = expandedStreet.street)
            query = query.filter(pollingDistrict = pollingDistrict.PollingDistrict)
            query = query.filter(numberFrom = expandedStreet.numberFrom)
            query = query.filter(numberTo = expandedStreet.numberTo)
            #print query.query
            results = list(query)

            if (len(results) == 0):
                nonExisting.append(expandedStreet)

        return nonExisting


    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianSeniunaitijaMembers)
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)
        reader = SeniunaitijaMembersReader(allRecords)

        fromPrint = 0
        toPrint = 9999999

        if len(args) > 0:
            if (args[0].find(":") > 0):
                split = args[0].split(':')
                fromPrint = int(split[0])
                try:
                    toPrint = int(split[1])
                except:
                    pass
            else:
                toPrint = int(args[0])

        streetExpander = SeniunaitijaAddressExpander()


        imported = 0
        totalNumberOfStreets = 0



        start = TimeMeasurer()
        #print "reading polling districts from %s to %s" % (fromPrint, toPrint)
        #allPollingDistricts = self.getPollingDistricts(aggregator, fromPrint, toPrint)

        #self.deletePollingDistrictsIfExists(allPollingDistricts)
        #print "pre-fetching constituencies"
        #self.preFetchAllConstituencies(allPollingDistricts)

        print "starting to import seniunaitija streets"
        wasError = 0
        count = 0
        for member in reader.ReadMembers():
            if (member.territoryStr == u""):
                continue
            if (member.seniunaitijaStr == u""):
                print "skipping teritory %s" % (member.uniqueKey)
                continue

            count += 1
            if (fromPrint > member.uniqueKey):
                continue
            if (toPrint < member.uniqueKey):
                break
            numberOfStreets = 0
            print "territory for: %s %s" % (member.uniqueKey, member.seniunaitijaStr)

            try:
                seniunaitija = Seniunaitija.objects.all().filter(id = member.uniqueKey)[0:1].get()
                for street in streetExpander.ExpandStreet(member.territoryStr):
                    numberOfStreets += 1
                    #print "street %s %s %s" %(numberOfStreets, street.city, street.street)
                    s = SeniunaitijaStreet()
                    s.municipality = member.municipalityStr
                    s.institution = seniunaitija
                    s.city = street.city
                    if s.city is None:
                        s.city = u""
                    s.street = street.street
                    if s.street is None:
                        s.street = u""
                    s.numberFrom = street.numberFrom
                    if street.numberFrom is not None:
                        s.numberOdd = street.numberFrom % 2
                    s.numberTo = street.numberTo
                    s.save()
            except Seniunaitija.DoesNotExist as e:
                logger.error(u"""Seniunaitija with id %s was not found""" % member.uniqueKey)
                wasError = wasError + 1
                continue
            except SeniunaitijaAddressExpanderException as e:
                logger.error(u"""Error in seniunaitija teritory nr '%s'
ErrorDetails = %s""" % (member.uniqueKey, e.message))
                wasError = wasError + 1
                continue

            imported += 1
            totalNumberOfStreets += numberOfStreets
            seconds = start.ElapsedSeconds()
            if seconds == 0:
                rate = "unknown"
            else:
                rate = str(totalNumberOfStreets / seconds)
            #print (u"%d: saved seniunaitija territory. Number of streets: '%d', \nTotal streets so far %d" % (count, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            #print "inserting at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)
            #print "\n\n"


        if wasError == 0:
            print u"succesfully imported %d seniunaitija territories, total %d streets" % (imported, totalNumberOfStreets)
        else:
            print u"Errors. Imported only part of the seniunaitija territories"
            print u"Imported %d seniunaitija territories, total %d streets" % (imported, totalNumberOfStreets)
            print u"There was %s errors" % (wasError)
        print u"total spent time %d seconds" % (start.ElapsedSeconds())
