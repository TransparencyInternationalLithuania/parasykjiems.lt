#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from cdb_lt_streets.models import LithuanianStreetIndexes
from django.db.models.query_utils import Q
import logging
from pjutils.deprecated import deprecated

logger = logging.getLogger(__name__)


wholeStreetEndings = [u"skersgatvis", u"kelias",
                    u"plentas", u"prospektas",
                    u"alėja", u"gatvė",
                    u"aikštė"]
shortStreetEndings = [u"skg.", u"kel.", u"pl.", u"pr.", u"al.", u"g.", u"a."]
allStreetEndings = wholeStreetEndings + shortStreetEndings


def removeGenericPartFromStreet(street):
    for e in wholeStreetEndings:
        if street.endswith(e):
            street = street.replace(e, u"")
    return street

def removeGenericPartFromMunicipality(municipality):
    endings = [u"miesto savivaldybė"]

    for e in endings:
        if municipality.endswith(e):
            municipality = municipality.replace(e, u"")
    return municipality

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

    def deduce(self, stringList):
        address = ContactDbAddress()

        parts = stringList.split(u",")
        if (self.containsNumber(parts[0])) or (self.containsStreet(parts[0])):
            address.street, address.number = self.extractStreetAndNumber(self.takePart(parts, 0))
            address.city = self.takePart(parts, 1)
            address.municipality = self.takePart(parts, 2)
        else:
            address.city = self.takePart(parts, 0)
            address.municipality = self.takePart(parts, 1)


        """for s in stringList:
            if (s.isdigit()):
                address.number += s
                continue

            isStreet = self.findStreet(s)
            if (isStreet):
                address.street += s
            isCity = self.findCity(s)
            if (isCity):
                address.city += s
            isMunicipality = self.findMunicipality(s)
            if (isMunicipality):
                address.municipality += s

            if (isCity == False and isStreet == False and isMunicipality == False ):
                address.unknown += s
                """

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
    addressContext = AddressDeducer().deduce(query_string)
    return addressContext



def searchInIndex(addressContext):
    """ """

    logger.debug("searching in index")
    logger.debug("addressContext %s" % ( addressContext.street))
    logger.debug("addressContext %s" % ( addressContext.city))
    logger.debug("addressContext %s" % ( addressContext.municipality))
    logger.debug("addressContext %s" % ( addressContext.number))

    #print "before filter %s %s %s" %(streetFilters, cityFilters)
    streetFilters = getOrQuery("street", addressContext.street)
    cityFilters = getOrQuery("city", addressContext.city)
    municipalityFilters = getOrQuery("municipality", addressContext.municipality)
    finalQuery = getAndQuery(streetFilters, cityFilters, municipalityFilters)
    #logger.debug("streetFilters %s" % (streetFilters))
    #logger.debug("cityFilters %s" % (cityFilters))
    #logger.debug("municipalityFilters %s" % (municipalityFilters))

    return LithuanianStreetIndexes.objects.filter(finalQuery).order_by('street')[0:50]