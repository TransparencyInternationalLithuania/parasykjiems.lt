#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import re
import os
from pjutils.exc import ChainnedException
from pjutils.deprecated import deprecated
from cdb_lt_mps.models import Constituency, Constituency
from cdb_lt_mps.parseConstituencies import ExpandedStreet

class ImportSourceNotExistsException(ChainnedException):
    pass

class ImportSources:
    LithuanianConstituencies = os.path.join("contactdb", "sources", "apygardos.txt")
    LithuanianMPs = os.path.join("contactdb", "sources", "parliament members.csv")
    LithuanianCivilParishMembers = os.path.join("contactdb", "sources", "LithuanianCivilParishMembers.csv")
    LithuanianMunicipalityMembers = os.path.join("contactdb", "sources", "LithuanianMunicipalityMembers.csv")
    LithuanianSeniunaitijaMembers  = os.path.join("contactdb", "sources", "LithuanianSeniunaitijaMembers.csv")
    LithuanianStreetIndex  = os.path.join("contactdb", "sources", "LithuanianStreetIndex.csv")
    LithuanianMunicipalities  = os.path.join("contactdb", "sources", "LithuanianMunicipalities.csv")

    @classmethod
    def EsnureExists(clas, importSource):
        """ Checks that a given import source exists on file system. if not, throw an exception,
         so that user would know how to donwload that source"""
        file = os.path.join(os.getcwd(), importSource)
        exists = os.path.exists(file)
        if (exists == False):
            raise ImportSourceNotExistsException("""File '%s' does not exist on your file system. Usually this means
that an appropriate google doc was not downloaded yet.  You can do that by calling manage.py downloadDocs """ % file) 

class GoogleDocsSources:
    """ collection of google docs documents for Lithuanian data"""

    # parliament members
    LithuanianMPs = "parasykjiems.lt 2"
    # Seniūnai / Foreman
    LithuanianCivilParishMembers = "parasykjiems.lt 3 seniunai"
    # Municipality mayors
    LithuanianMunicipalityMembers = "parasykjiems.lt 4 merai"
    # Seniūnaičiai
    LithuanianSeniunaitijaMembers = "parasykjiems.lt 5 seniunaiciai"

    LithuanianStreetIndex = "Lithuanian street index"
    LithuanianMunicipalities = "Contact DB LT Municipalities"


class SeniunaitijaAddressExpanderException(ChainnedException):
    pass

class SeniunaitijaAddressExpander:
    streetPrefixes = [u'mstl.', u'k.', u'vs.']

    def GetCityPrefix(self, city, prefix):
        if (prefix == "mstl."):
            return "%s %s" % (city, "miestelis")
        return "%s %s" % (city, prefix)

    def ContainsCity(self, street):
        for prefix in self.streetPrefixes:
            index = street.find(prefix)
            if (index >= 0):
                city = street[0:index].strip()
                city = self.GetCityPrefix(city, prefix)
                streetNew = street[index + len(prefix):].strip()
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

    def RemoveLetter(self, fromNumber):
        # maybe it contains letter
        m = re.search('[a-zA-Z]', fromNumber)
        if (m is not None):
            group = m.group()
            letterFrom = group
            fromNumber = fromNumber.replace(group, "")
        return fromNumber

    def ContainsNumbers(self, fromNumber):
        m = re.search('[0-9]', fromNumber)
        if (m is not None):
            return True
        return False

    def ExpandStreet(self, streets):
        """ yield a ExpandedStreet object for each house number found in street """

        if (streets == "" or streets is None):
            yield ExpandedStreet(street = u"")
            return

        if (streets.strip() == ""):
            yield ExpandedStreet(street = u"")
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
                    if (self.ContainsNumbers(street) == True):
                        streetProperties = street
                        street = lastStreet
                    else:
                        city = street
                        streetProperties = None
                        street = None
                else:
                    street = None

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
                            numberFrom = self.RemoveLetter(numberFrom)
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
                                numberTo = self.RemoveLetter(numberTo)
                                numberTo = int(numberTo)
                        except:
                            raise SeniunaitijaAddressExpanderException("could not convert string '%s' to number" % numberTo)

                        yield ExpandedStreet(street = street, city = city, numberFrom = numberFrom, numberTo = numberTo)
                    # we have yielded already, continue
                    lastStreet = street
                    continue

                else:
                    # else it will be simple number
                    if (self.ContainsNumbers(streetProperties) == False):
                        raise SeniunaitijaAddressExpanderException("string '%s' does not contain numbers. Though i expected it to be a house number" % streetProperties)

                    streetProperties = self.RemoveLetter(streetProperties)
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
