#!/usr/bin/env python
# -*- coding: utf8 -*-

import copy
from pjutils.exc import ChainnedException
from contactdb.models import Constituency
from pjutils.deprecated import deprecated

class ImportSources:
    LithuanianConstituencies = "contactdb/sources/apygardos.txt"
    LithuanianMPs = "contactdb/sources/parliament members.txt"

class GoogleDocsSources:
    """ collection of google docs documents for Lithuanian data"""

    # parliament members
    LithuanianMPs = "parasykjiems.lt 2"






# simply introducing an enumartion, so that we can use
# this as states when reading file.
# Probably might be a better way to do this in python
class State:
    # values here does not mean anything at all
    District = "d"
    Constituency = "c"
    PollingDistrict = "ec"
    Addresses = "ad"



class PollingDistrictLocation:
    """a DTO which is returned for eaach location read in the Lithuanian Counties file.
    The difference from PollingDistrictStreet is that this class contains non-parsed
    street data. Before inserting into database we need to parse Addresses field into
    separate streets.
    """
    # rajonas
    District = ""
    # apygarda
    Constituency = None
    # apylinkė
    PollingDistrict = ""
    Addresses = ""
    pollingDistrictAddress = None
    numberOfVoters = None

    # how to convert python object to string?
    # dont know yet, so using this hack :)
    # we could also iterate over all "fields??" in this object
    # but how to do that??
    def __str__(self):
        return "District: " + self.District + "\nConstituency " + self.Constituency + "\nPollingDistrict " + self.PollingDistrict + "\nAddresses " + self.Addresses


class LithuanianConstituencyAggregator:
    """ Aggregates PollingDistrictLocation objects and returns only unique Counties"""
    def __init__(self, file):
        self.file = file
        self.importer = LithuanianCountyReader(file)
        self.allCounties = []

        self._readAll()

    def _readAll(self):
        for loc in self.importer.getLocations():
            self.allCounties.append(loc)

    def GetDistinctConstituencies(self):
        """                                                                                          pksvdd1199aatg1a
        Returns a list of string for each distinct Constituency
        """
        counties = {}
                           
        for c in self.allCounties:
            exist = c.County.name in counties
            if (exist == False):
                counties[c.County.name] = c
                yield c.County
            
        
        

class NotFoundConstituencyNrException(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)

class LithuanianConstituencyParser:

    def ExtractConstituencyFromMPsFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian MPs file """
        lower = constituencyString.lower()
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundCountyNrException("Could not parse county nr in string '%(s)s'" % {"s" : lower})
        c = Constituency()
        c.name = constituencyString[:nr].strip(" (")
        c.nr =  int(constituencyString[nr + 3: ].strip(" )"))
        return c

    def ExtractConstituencyFromCountyFile(self, countyString):
        """Extracts a Constituency object from a Lithuanian Constituency file"""
        lower = countyString.lower()
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundCountyNrException("Could not parse county nr in string '%(string)s'") % {"string" : lower}
        c = Constituency()
        c.name = countyString[:nr].strip(" ")
        c.nr =  int(countyString[nr + 3: ])
        return c


class LithuanianCountyReader:
    """ Reads Lithuanian counties from file. Gives a generator function
    which returns a single PollingDistrictLocation instance for each smallest object
    defined in file( PollingDistrict/ (rinkimų apylinkė)
    """
    def __init__(self, file):
        """Pass an opened file containing Lithuanian Counties (Apygardos)."""
        self.file = file
        self.countyParser = LithuanianConstituencyParser()

    @deprecated
    def _ConsumeNonEmptyLines(self, numberOfLines):
        for i in range(1, numberOfLines):
            self._notEmptyLine()

    # a function which returns only non empty
    # lines specific for Lithuanian municipality files.
    def _notEmptyLine(self):

        # read a line from file
        for s in self.file:

            # return each splited line as separate line
            s = self._removeDumbCharacters(s)
            if (s == ""):
                continue
            return s

        return ""

    def _removeDumbCharacters(self, str):
        return str.strip("* \r\n")

    def _readAddress(self):
        strings = []
        # read first non empty line. This ensures that all blank lines are skipped
        strings.append(self._notEmptyLine())

        # read all non empty lines, and append to list
        # when empty strins is found, that means addresses are finished
        for s in self.file:
            s = self._removeDumbCharacters(s)
            if (s == ""):
                break
            strings.append(s)
            strings.append(" ")

        return "".join(strings)

    def readParagraph(self):
        s = ""
        for s in self.file:
            s = self._removeDumbCharacters(s)
            if s != "":
                break

        adr = []
        adr.append(s)
        for s in self.file:
            s = self._removeDumbCharacters(s)
            if s == "":
                break
            adr.append(s)

        return " ".join(adr)

    # a generator which returns a PollingDistrictLocation object
    # for each election district defined in the file
    def getLocations(self):
        state = State.District
        location = PollingDistrictLocation()
        while (1):
            line = self._notEmptyLine()

            if (line == ""):
                return

            if (line.find("apygarda") >=0 ):
                location.County = self.countyParser.ExtractConstituencyFromCountyFile(line)
                state = State.PollingDistrict
                continue

            if (line.find("apylink") >=0 ):
                location.PollingDistrict = line
                state = State.Addresses

                if (line.find("S. Daukanto rinkimų apylinkė Nr. 64") >= 0):
                    print state

                # this county is special, since it has no streets.
                # So just instruct so skip reading streets for this county
                # HACK for now, but works
                # If you remove it, a test will fail
                if (line.find("Jūreivių rinkimų apylinkė") >=0 ):
                    yield location
                    state = State.Constituency
                    continue

                location.pollingDistrictAddress = self.readParagraph()
                location.numberOfVoters = self.readParagraph()
                #self._ConsumeNonEmptyLines(2)

                location.Addresses = self._readAddress()
                state = State.District
                clone = copy.copy(location)
                yield clone

                continue

            if state == State.District:
                location.District = line
                state = State.Constituency
                continue