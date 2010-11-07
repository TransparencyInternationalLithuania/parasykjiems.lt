#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pjutils.uniconsole import *
import re
from cdb_lt_streets.models import LithuanianStreetIndexes
from django.db.models.query_utils import Q
import logging
from pjutils.deprecated import deprecated

logger = logging.getLogger(__name__)


wholeStreetEndings = [u"skersgatvis", u"kelias",
                    u"plentas", u"prospektas",
                    u"alėja", u"gatvė",
                    u"aikštė", u"takas"]
shortStreetEndings = [u"skg.", u"kel.", u"tak.", u"pl.", u"pr.", u"al.", u"g.", u"a."]
allStreetEndings = wholeStreetEndings + shortStreetEndings

wholeMunicipalityEndings = [u"miesto savivaldybė"]
shortMunicipalityEndings = [u"m. sav."]
allMunicipalityEndings = wholeMunicipalityEndings + shortMunicipalityEndings

def removeGenericPartFromStreet(street):
    if (street is None):
        return ""
    for e in allStreetEndings:
        if street.endswith(e):
            street = street.replace(e, u"")
    return street.strip()

def removeGenericPartFromMunicipality(municipality):
    for e in allMunicipalityEndings:
        if municipality.endswith(e):
            municipality = municipality.replace(e, u"")
    return municipality.strip()

class ContactDbAddress:
    def __init__(self):
        self.street = u""
        self.city = u""
        self.municipality = u""
        self.unknown = u""
        self.number = u""


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

    def extractStreetAndNumber(self, streetWithNumber):
        parts = streetWithNumber.split(u" ")
        number = [p for p in parts if p.isdigit() == True]
        number = " ".join(number)
        number = number.strip()

        street = [p for p in parts if p.isdigit() == False]
        street = " ".join(street)
        street = street.strip()
        return (street, number)

    def containsNumber(self, str):
        parts = str.split(" ")
        for p in parts:
            if p.isdigit():
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

    def deduce(self, stringList):
        address = ContactDbAddress()

        if (stringList.find(u",") >= 0):
            parts = stringList.split(u",")
            # if first part contains either number, or street, thet it is street, city, municipality
            if (self.containsNumber(parts[0])) or (self.containsStreet(parts[0])):
                address.street, address.number = self.extractStreetAndNumber(self.takePart(parts, 0))
                address.city = self.takePart(parts, 1)
                address.municipality = self.takePart(parts, 2)
            else:
                # else this is city, and municipality only
                address.city = self.takePart(parts, 0)
                address.municipality = self.takePart(parts, 1)
        else:
            parts = self.splitNoCommas(stringList)
            if (self.containsNumber(parts[0])) or (self.containsStreet(parts[0])):
                address.street, address.number = self.extractStreetAndNumber(self.takePart(parts, 0))
                address.city = self.takePart(parts, 1)
                address.municipality = self.takePart(parts, 2)
            else:
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



def getOrQuery(fieldName, fieldValues):
    streetFilters = None
    for s in fieldValues:
        q = Q(**{"%s__icontains" % fieldName: s})
        if streetFilters is None:
            streetFilters = q
        else:
            streetFilters = streetFilters | q
    return streetFilters

def getAndQuery(*args):
    finalQuery = None
    for q in args:
        if (q is None):
            continue
        if (finalQuery is None):
            finalQuery = q
        else:
            finalQuery = finalQuery & q
    return finalQuery


def deduceAddress(query_string):
    """ parses a given string into a house number, street, city and municipality parts
    Return result is type of ContactDbAddress """
    addressContext = AddressDeducer().deduce(query_string)
    return addressContext



def searchInIndex(addressContext):
    """ Searches for streets using a given address."""

    logger.debug(u"searching in index")
    logger.debug(u"addressContext.number '%s'" % ( addressContext.number))
    logger.debug(u"addressContext.street '%s'" % ( addressContext.street))
    logger.debug(u"addressContext.city '%s'" % ( addressContext.city))
    logger.debug(u"addressContext.municipality '%s'" % ( addressContext.municipality))

    street = removeGenericPartFromStreet(addressContext.street)
    municipality = removeGenericPartFromMunicipality(addressContext.municipality)
    city = addressContext.city

    logger.debug(u"street %s" % ( street))
    logger.debug(u"city %s" % ( city))
    logger.debug(u"municipality %s" % ( municipality))

    #print "before filter %s %s %s" %(streetFilters, cityFilters)
    streetFilters = getOrQuery("street", [street])
    cityFilters = getOrQuery("city", [city])
    municipalityFilters = getOrQuery("municipality", [municipality])
    finalQuery = getAndQuery(streetFilters, cityFilters, municipalityFilters)
    #logger.debug("streetFilters %s" % (streetFilters))
    #logger.debug("cityFilters %s" % (cityFilters))
    #logger.debug("municipalityFilters %s" % (municipalityFilters))
    query = LithuanianStreetIndexes.objects.filter(finalQuery).order_by('street')[0:50]
    #logger.debug(query.query)
    return query