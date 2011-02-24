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
        wasPreviousStreet = False
        for s in words:
            # Handle also this case : gaidžių g. vilnius
            # After city part, there is no street number, so explicitly check for that
            # if we do not find street number, that means street part is finisehd, so go to next block
            if wasPreviousStreet == True:
                if self.containsAnyNumber(s) == False:
                    wasNumber = True
            
            if wasNumber == False:
                firstPart.append(s)
                if self.containsAnyNumber(s):
                    wasNumber = True
                    continue

            if wasNumber == True:
                if self.containsStreet(s):
                    firstPart.append(s)
                else:
                    secondPart.append(s)
            
            wasPreviousStreet = self.containsStreet(s)

        firstPart = " ".join(firstPart)
        secondPart = " ".join(secondPart)
        return firstPart, secondPart

    def splitIntoCityAndMunicipality(self, string):
        string = string.strip()
        splitted = string.split(u" ")
        splitted = [p for p in splitted if p.strip() != u""]
        # if we have less than two words, just return what we have
        if len(splitted) < 2:
            return splitted
        # first part is always city name

        wasCity = -1
        for i in range(1, len(splitted)):
            if splitted[i] in allCityEndings:

                # This is not accurate, since address Vilnius, Viniaus m. sav. will fail
                # the first part is the city, and the second is municipality. But note that
                # municipality part contains "m." part, which is a city ending in short form
                # so just check if "sav." follows it, which stands for "municipality"
                if i + 1< len(splitted):
                    next = splitted[i+1]
                    if next == u"sav.":
                        continue
                wasCity = i


        if wasCity == -1:
            wasCity = 0;

        cityString = " ".join(splitted[0:wasCity + 1])
        allElse = u" ".join(splitted[wasCity + 1:])
        return [cityString, allElse]







    def deduce(self, stringList):
        address = ContactDbAddress()

        if stringList.find(u",") >= 0:
            parts = stringList.split(u",")
            # if first part contains either number, or street, then it is street, city, municipality
            if (self.containsNumber(parts[0])) or (self.containsStreet(parts[0])) or (self.containsAnyNumber(parts[0])):
                address.street, address.number, address.flatNumber  = self.extractStreetAndNumber(self.takePart(parts, 0))

                # combine everything else again into string
                joined = u" ".join(parts[1:])
                # and then extract city and municipality
                parts = self.splitIntoCityAndMunicipality(joined)
                address.city = self.takePart(parts, 0)
                address.municipality = self.takePart(parts, 1)
            else:
                # else this is city, and municipality only
                address.city = self.takePart(parts, 0)
                address.municipality = self.takePart(parts, 1)
        else:
            # try treating as if it a street with number
            firstPartWithNumber, everythingElse = self.splitFirstNumberAndEverythingElse(stringList)
            
            if self.containsAnyNumber(firstPartWithNumber) or self.containsStreet(firstPartWithNumber):
                address.street, address.number, address.flatNumber = self.extractStreetAndNumber(firstPartWithNumber)
                everythingElse = self.splitIntoCityAndMunicipality(everythingElse)
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

def searchInIndex(municipality = None, city = None, street = None):
    """ Search what kind of addresses exist in our street index.
     Usually you call this function when you want to be sure that the values are real, and not some
     random data (usually entered by user). Use function deduceAddress(query_string) to parse a user input
     and then call this function to get a result list, for ex

     addressContext = deduceAddress(query_string)
     found_entries = searchInIndex(municipality= addressContext.municipality, city= addressContext.city,
                                  street= addressContext.city, house_number= addressContext.number,
                                  flatNumber= addressContext.flatNumber)

    each record in found_entries is an instance of LithuanianStreetIndexes. If result is one, then there
    is only one exact match. If more, then user should probably narrow his search, or pick from the list.

    """
    if municipality is not None:
        municipality = municipality.capitalize()
        municipality = municipality.strip()
        if municipality == u"":
            municipality = None

    if municipality is not None:
        municipality = getGenericCaseMunicipality(municipality)

    if street is not None:
        if len(street) >1:
            # capitalise, and presereve other uppercase letters
            street = street[0].upper() + street[1:]
        street = street.strip()
        if street == u"":
            street = None

    logger.debug(u"searching in index")
    logger.debug(u"addressContext.street '%s'" % street)
    logger.debug(u"addressContext.city '%s'" % city)
    logger.debug(u"addressContext.municipality '%s'" % municipality)


    # Lithuanian cities have cities in two forms - genitive and nominative
    city = city.capitalize()
    cityQuery = None
    if not (city == u"" or city == None):
        cityQuery_Nominative = Q(**{"city__icontains": city})
        cityQuery_Genitive = Q(**{"city_genitive__icontains": city})
        cityQuery = cityQuery_Genitive | cityQuery_Nominative
        
    municipalityQuery = None
    if municipality is not None:
        municipalityQuery = Q(**{"municipality__icontains": municipality})
    #streetFiltersStartsWith = Q(**{"street__istartswith" : street})

    if street is None:
        finalQuery = getAndQuery(cityQuery, municipalityQuery)
        return LithuanianStreetIndexes.objects.all().filter(finalQuery)\
        .order_by('street')[0:50]
    else:
        # try searching with istarts with on whole street
        # just transform short street ending to long form
        street = changeStreetFromShortToLongForm(street)
        streetStartsWithEnding = q = Q(**{"street__istartswith": street})
        streetExactWithEndingFilter = getAndQuery(municipalityQuery, cityQuery, streetStartsWithEnding)
        streetExactWithEnding = LithuanianStreetIndexes.objects.all().filter(streetExactWithEndingFilter)\
            .order_by('street')[0:50]
        streetExactWithEnding = list(streetExactWithEnding)
        if len(streetExactWithEnding) > 0:
            return streetExactWithEnding


        streetEnding = extractStreetEndingForm(street)
        streetWihoutEnding = removeGenericPartFromStreet(street)
        streetWihoutEndingQueryStartsWith = Q(**{"street__istartswith": streetWihoutEnding})
        streetEndingQuery = None
        if streetEnding is not None:
            streetEndingQuery = Q(**{"street__icontains": streetEnding})

        # search for street without stripped street ending, and street ending as separate query
        streetExactFilter = getAndQuery(municipalityQuery, cityQuery, streetWihoutEndingQueryStartsWith, streetEndingQuery)
        streetExact = LithuanianStreetIndexes.objects.all().filter(streetExactFilter)\
            .order_by('street')[0:50]
        streetExact = list(streetExact)
        if len(streetExact) > 0:
            return streetExact

        # find with exact street
        streetExactFilter = getAndQuery(municipalityQuery, cityQuery, streetWihoutEndingQueryStartsWith)
        streetExact = LithuanianStreetIndexes.objects.all().filter(streetExactFilter)\
            .order_by('street')[0:50]
        streetExact = list(streetExact)
        if len(streetExact) > 0:
            return streetExact

        #search for street without using street ending and starts with
        streetExactFilter = getAndQuery(municipalityQuery, cityQuery, streetWihoutEndingQueryStartsWith)
        streetExact = LithuanianStreetIndexes.objects.all().filter(streetExactFilter)\
            .order_by('street')[0:50]
        streetExact = list(streetExact)
        if len(streetExact) > 0:
            return streetExact

        #search for street without using street ending   and starts icontains
        streetWihoutEndingQueryContains = Q(**{"street__icontains": streetWihoutEnding})
        streetWithoutEndingFilter = getAndQuery(municipalityQuery, cityQuery, streetWihoutEndingQueryContains)
        streetWithouEndingResult = LithuanianStreetIndexes.objects.all().filter(streetWithoutEndingFilter)\
            .order_by('street')[0:50]
        if len(streetWithouEndingResult) > 0:
            return streetWithouEndingResult


        # search by street failed. Try searching wihout street
        finalQuery = getAndQuery(cityQuery, municipalityQuery)
        if finalQuery == None:
            return []
        return LithuanianStreetIndexes.objects.all().filter(finalQuery)\
            .order_by('street')[0:50]
