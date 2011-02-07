#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pjutils.uniconsole import *
import re
from cdb_lt_streets.models import LithuanianStreetIndexes, LithuanianCases
from django.db.models.query_utils import Q
import logging
from pjutils.deprecated import deprecated
from ltPrefixes import *
from pjutils.queryHelper import getAndQuery, getOrQuery
from cdb_lt_streets.houseNumberUtils import isStringStreetHouseNumber

logger = logging.getLogger(__name__)

class ContactDbAddress:
    def __init__(self):
        self.street = u""
        self.city = u""
        self.municipality = u""
        self.unknown = u""
        # house number
        self.number = u""
        self.flatNumber = u""

class AddressDeducer():
    """ Deduces which strings are city, which street, and which is municipality """

    def findStreet(self, streetName):
        length = len(LithuanianStreetIndexes.objects.filter(street__icontains = streetName))
        return length > 0

    def findCity(self, streetName):
        length = len(LithuanianStreetIndexes.objects.filter(city__icontains = streetName))
        return length > 0

    def findMunicipality(self, streetName):
        length = len(LithuanianStreetIndexes.objects.filter(municipality__icontains = streetName))
        return length > 0


    def takePart(self, parts, pos):
        if (len(parts) > pos):
            return parts[pos].strip()
        return ""

    def _splitByHyphenAndSpace(self, string):
        # string such as "Sausio 13-osios g., vilnius" must be split only by spaces, since the number is not a house
        # number and flat number
        # string "Gedimino 15-13, vilnius" will be split by hyphen, since it is a flat number and house number
        parts = string.split(u" ")
        final = []
        for p in parts:
            if (p.find('-') == -1):
                final.append(p)
            else:
                p1, p2 = p.split('-')
                if p1.isdigit() and p2.isdigit():
                    final.append(p1)
                    final.append(p2)
                else:
                    final.append(p)
        return final

    def extractStreetAndNumber(self, streetWithNumber):
        number = ""
        flatNumber = ""

        parts = self._splitByHyphenAndSpace(streetWithNumber)
        digits = [d for d in parts if isStringStreetHouseNumber(d)]
        if (len(digits) > 0):
            number = digits[0]
        if (len(digits) > 1):
            flatNumber = digits[1]

        street = [p for p in parts if isStringStreetHouseNumber(p) == False]
        street = " ".join(street)
        street = street.strip()
        return (street, number, flatNumber)

    def containsNumber(self, str):
        """ check if string contains a house number. String is split by hyphen and space first"""
        parts = self._splitByHyphenAndSpace(str)
        for p1 in parts:
            if isStringStreetHouseNumber(p1):
                return True
        return False

    def containsAnyNumber(self, str):
        """ returns if string contains number anywhere in the string"""
        m = re.search('[0-9]', str)
        if (m is not None):
            return True
        return False
        

    def containsStreet(self, str):
        for ending in allStreetEndings:
            if str.find(ending) >= 0:
                return True
        return False

    def splitNoCommas(self, str):
        """ when an address is entered without commas, use some custom logic to split it into parts"""
        returnList = []
        parts = str.split(u" ")
        containsNumbers = False
        for p in parts:
            if (self.containsStreet(p) or self.containsNumber(p)):
                containsNumbers = True

        if (containsNumbers == False):
            returnList.append(parts[0])
            rest = u" ".join(parts[1:])
            rest = rest.strip()
            returnList.append(rest)
            return returnList

        current = parts[0]
        i = 0
        i1 = 1
        while i1 < len(parts):
            next = parts[i1]
            if self.containsStreet(next) or self.containsNumber(next):
                current = u"%s %s" % (current, next)
            else:
                break
            i1 += 1
            i += 1
        returnList.append(current)
        if (len(parts) > i + 1):
            returnList.append(parts[i + 1])
        rest = u" ".join(parts[i + 2:])
        rest = rest.strip()
        returnList.append(rest)
        return returnList

    def splitFirstNumberAndEverythingElse(self, str):
        """ examines a string, and divides it into 2. First part is everything up to first word with number,
        and then the rest. For example having str 'Verkių g. 30 Vilnius Vilniaus m. sav.'
        first part will be 'Verki7 g. 30', and 'Vilnius Vilniaus m. sav.' as everything else.

        'Sausio 13-osios gatvė' will be only first part, rest part will be empty
        """

        wasNumber = False
        words = str.split(u" ")
        firstPart = []
        secondPart = []
        for s in words:
            if (wasNumber == False):
                firstPart.append(s)
                if self.containsAnyNumber(s):
                    wasNumber = True
                    continue

            if (wasNumber == True):
                if (self.containsStreet(s)):
                    firstPart.append(s)
                else:
                    secondPart.append(s)

        firstPart = " ".join(firstPart)
        secondPart = " ".join(secondPart)
        return firstPart, secondPart

    def splitIntoCityAndMunicipality(self, string):
        splitted = string.split(" ")
        # if we have less than two words, just return what we have
        if (len(splitted) < 2):
            return splitted
        # first part is always city name
        cityString = [splitted[0]]

        # if second part is one of the generic city endings, append it to city name
        # such as instead of 'new york", return "new york city" + everything else
        if (splitted[1] in allCityEndings):
            cityString.append(splitted[1])
            cityString = " ".join(cityString)
            return [cityString] + splitted[2:]

        # return everything else, since only the second part can be city ending
        return splitted







    def deduce(self, stringList):
        address = ContactDbAddress()

        if (stringList.find(u",") >= 0):
            parts = stringList.split(u",")
            # if first part contains either number, or street, then it is street, city, municipality
            if (self.containsNumber(parts[0])) or (self.containsStreet(parts[0])) or (self.containsAnyNumber(parts[0])):
                address.street, address.number, address.flatNumber  = self.extractStreetAndNumber(self.takePart(parts, 0))
                address.city = self.takePart(parts, 1)
                address.municipality = self.takePart(parts, 2)
            else:
                # else this is city, and municipality only
                address.city = self.takePart(parts, 0)
                address.municipality = self.takePart(parts, 1)
        else:
            # try treating as if it a street with number
            firstPartWithNumber, everythingElse = self.splitFirstNumberAndEverythingElse(stringList)
            
            if self.containsAnyNumber(firstPartWithNumber) or self.containsStreet(firstPartWithNumber):
                address.street, address.number, address.flatNumber = self.extractStreetAndNumber(firstPartWithNumber)
                everythingElse = self.splitNoCommas(everythingElse)
                address.city = self.takePart(everythingElse, 0)
                address.municipality = self.takePart(everythingElse, 1)
            else:
                parts = self.splitIntoCityAndMunicipality(stringList)
                # else this is city, and municipality only
                address.city = self.takePart(parts, 0)
                address.municipality = self.takePart(parts, 1)

        return address


@deprecated
class AddressCruncher:
    """ Crunches address and removes any dummy words """
    def __init__(self):
        pass

    """ Returns a list of key words extracted from query string"""
    def crunch(self, query_string):
        qery_list = re.split(r'[ ,]', query_string)

        # remove empty words
        qery_list = [l for l in qery_list if l.strip() != u""]
        # remove words less than 3 letters
        # but keep numbers
        qery_list = [l for l in qery_list if (l.isalpha() and len(l) < 3) == False]
        return qery_list


def deduceAddress(query_string):
    """ parses a given string into a house number, street, city and municipality parts
    Return result is type of ContactDbAddress """
    addressContext = AddressDeducer().deduce(query_string)
    return addressContext


def getGenericCaseMunicipality(municipalityNominative):

    mun = LithuanianCases.objects.all().filter(institutionType = LithuanianCases.Type.Municipality)\
        .filter(nominative__icontains = municipalityNominative)[0:1]
    if len(mun) == 0:
        return municipalityNominative
    return mun[0].genitive

def searchInIndex(addressContext):
    """ Searches for streets using a given address."""

    addressContext.city = addressContext.city.capitalize()
    addressContext.street = addressContext.street.capitalize()

    logger.debug(u"searching in index")
    logger.debug(u"addressContext.flatNumber '%s'" % ( addressContext.flatNumber))
    logger.debug(u"addressContext.number '%s'" % ( addressContext.number))
    logger.debug(u"addressContext.street '%s'" % ( addressContext.street))
    logger.debug(u"addressContext.city '%s'" % ( addressContext.city))
    logger.debug(u"addressContext.municipality '%s'" % ( addressContext.municipality))

    city = addressContext.city
    street = addressContext.street
    street = changeStreetFromShortToLongForm(street)
    #street = removeGenericPartFromStreet(addressContext.street)
    city = changeCityFromShortToLongForm(city)
    municipality = removeGenericPartFromMunicipality(addressContext.municipality)


    if municipality is not None and municipality != u"":
        municipality = getGenericCaseMunicipality(municipality)

    logger.debug(u"street %s" % ( street))
    logger.debug(u"city %s" % ( city))
    logger.debug(u"municipality %s" % ( municipality))

    #print "before filter %s %s %s" %(streetFilters, cityFilters)
    streetFilters = q = Q(**{"street__icontains": street})
    # Lithuanian cities have cities in two forms - genitive and nominative
    cityFilters = Q(**{"city__icontains": city}) 
    cityFiltersGenitive = Q(**{"city_genitive__icontains": city})
    municipalityFilters = Q(**{"municipality__icontains": municipality})
    streetFiltersStartsWith = Q(**{"street__istartswith" : street})

    # search search with street istarts with
    finalQueryStartsWith = getAndQuery(streetFiltersStartsWith, cityFilters | cityFiltersGenitive, municipalityFilters)
    results = list(LithuanianStreetIndexes.objects.filter(finalQueryStartsWith).order_by('street')[0:50])
    if len(results) > 0:
        return results
    

    # if not, search with street icontains
    finalQuery = getAndQuery(streetFilters, cityFilters | cityFiltersGenitive, municipalityFilters)
    #logger.debug("streetFilters %s" % (streetFilters))
    #logger.debug("cityFilters %s" % (cityFilters))
    #logger.debug("municipalityFilters %s" % (municipalityFilters))
    query = LithuanianStreetIndexes.objects.filter(finalQuery).order_by('street')[0:50]
    #logger.debug(query.query)
    return list(query)