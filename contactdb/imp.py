#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from pjutils.exc import ChainnedException
from contactdb.models import Constituency
from pjutils.deprecated import deprecated

class ImportSources:
    LithuanianConstituencies = "contactdb/sources/apygardos.txt"
    LithuanianMPs = "contactdb/sources/parliament members.txt"
    LithuanianCivilParishMembers = "contactdb/sources/LithuanianCivilParishMembers.csv"
    LithuanianMunicipalityMembers = "contactdb/sources/LithuanianMunicipalityMembers.csv"
    LithuanianSeniunaitijaMembers  = "contactdb/sources/LithuanianSeniunaitijaMembers.csv"

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


class PollingDistrictStreetExpander:
    """ When PollingDistrictStreets are parsed from txt file, some streets are subidivied into house numbers.
    Here are a few examples of how these look like:
    Stoties g.
    Respublikos g. Nr. 18; Nr. 20; Nr. 21; Nr. 23; Nr. 24; Nr. 25; Nr. 27
    Respublikos g. Nr. 19; Nr. 26; Nr. 28; numeriai nuo Nr.1 iki Nr. 17
    S. Dariaus ir S. Girėno g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 4 iki galo
    etc

    Expander will parse and return a tuple for each row separately
    """

    def ExpandStreet(self, street):
        """ yield a tuple(street, house numbe) for each house number found in street """


        if (street == "" or street == None):
            yield ("", "")
            return

        street = street.strip()
        # if no street nr, return single tuple
        if (street.find("Nr") < 0):
            yield (street, "")
            return

        streets = street.split("g.")
        str = streets[0].strip()
        str = "%s g." % str
        nrs = streets[1].split("Nr.")
        for nr in nrs:
            nr = nr.replace(";", "")
            nr = nr.strip()
            if (nr == ""):
                continue
            yield (str, nr)



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
    """a DTO which is returned for eaach location read in the Lithuanian Constituencies file.
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
    """ Aggregates PollingDistrictLocation objects and returns only unique Constituencies"""
    def __init__(self, file):
        self.file = file
        self.importer = LithuanianConstituencyReader(file)
        self._allConstituencies = []

        self._readAll()

    def _readAll(self):
        for loc in self.importer.getLocations():
            self._allConstituencies.append(loc)

    def GetDistinctConstituencies(self):
        """                                                                                          pksvdd1199aatg1a
        Returns a list of string for each distinct Constituency
        """
        constituencies = {}
                           
        for c in self._allConstituencies:
            exist = c.Constituency.name in constituencies
            if (exist == False):
                constituencies[c.Constituency.name] = c
                yield c.Constituency
            
        
        

class NotFoundConstituencyNrException(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)

class LithuanianConstituencyParser:

    def ExtractConstituencyFromMPsFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian MPs file """
        lower = constituencyString.lower()

        # išrinktas pagal sąrašą means that MP does not have a constituency
        if (lower.find("pagal sąrašą") > 0):
            return None
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundConstituencyNrException("Could not parse Constituency nr in string '%(s)s'" % {"s" : lower})
        c = Constituency()
        c.name = constituencyString[:nr].strip(" (")
        c.nr =  int(constituencyString[nr + 3: ].strip(" )"))
        return c

    def ExtractConstituencyFromConstituencyFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian Constituency file"""
        lower =  constituencyString.lower()
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundConstituencyNrException("Could not parse constituency nr in string '%(string)s'") % {"string" : lower}
        c = Constituency()
        c.name =  constituencyString[:nr].strip(" ")
        c.nr =  int( constituencyString[nr + 3: ])
        return c


class LithuanianConstituencyReader:
    """ Reads Lithuanian counties from file. Gives a generator function
    which returns a single PollingDistrictLocation instance for each smallest object
    defined in file( PollingDistrict/ (rinkimų apylinkė)
    """
    def __init__(self, file):
        """Pass an opened file containing Lithuanian Counties (Apygardos)."""
        self.file = file
        self.constituencyParser = LithuanianConstituencyParser()

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
                location.Constituency = self.constituencyParser.ExtractConstituencyFromConstituencyFile(line)
                state = State.PollingDistrict
                continue

            if (line.find("apylink") >=0 ):
                location.PollingDistrict = line
                state = State.Addresses

                if (line.find("S. Daukanto rinkimų apylinkė Nr. 64") >= 0):
                    print state

                # this Constituency is special, since it has no streets.
                # So just instruct so skip reading streets for this Constituency
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
