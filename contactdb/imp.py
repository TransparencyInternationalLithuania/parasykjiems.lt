#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import re
import os
from pjutils.exc import ChainnedException
from contactdb.models import Constituency
from pjutils.deprecated import deprecated

class ImportSourceNotExistsException(ChainnedException):
    pass

class ImportSources:
    LithuanianConstituencies = os.path.join("contactdb", "sources", "apygardos.txt")
    LithuanianMPs = os.path.join("contactdb", "sources", "parliament members.txt")
    LithuanianCivilParishMembers = os.path.join("contactdb", "sources", "LithuanianCivilParishMembers.csv")
    LithuanianMunicipalityMembers = os.path.join("contactdb", "sources", "LithuanianMunicipalityMembers.csv")
    LithuanianSeniunaitijaMembers  = os.path.join("contactdb", "sources", "LithuanianSeniunaitijaMembers.csv")

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

class PollingDistrictStreetExpanderException(ChainnedException):
    pass


class ExpandedStreet(object):


    """ The biggest house number that can possibly exist. This is usually used
    when in address range is refered in this form "from number 5 till the end".
    So the end in this case is this number"""
    MaxOddValue = 999999
    MaxEvenValue = 999999 - 1

    def __init__(self, street, numberFrom = None, numberTo = None):
        self.street = street
        self.numberFrom = numberFrom
        self.numberTo = numberTo

class PollingDistrictStreetExpander:
    """ When PollingDistrictStreets are parsed from txt file, some streets are subidivied into house numbers.
    Here are a few examples of how these look like:
    Stoties g.
    Respublikos g. Nr. 18; Nr. 20; Nr. 21; Nr. 23; Nr. 24; Nr. 25; Nr. 27
    Respublikos g. Nr. 19; Nr. 26; Nr. 28; numeriai nuo Nr.1 iki Nr. 17
    S. Dariaus ir S. Girėno g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 4 iki galo
    etc

    Expander will parse and return a ExpandedStreet object for each row separately
    """

    def _RemoveStreetPart(self, part, streetPartName):
        if (part.find(streetPartName) >= 0):
            noName = part.split(streetPartName)
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s %s" % (str, streetPartName)
            part = noName[-1]
            return (part, str)
        return None

    def _RemoveStreetPartSB(self, part, streetPartName):
        if (part.find(streetPartName) >= 0):
            noName = part.split("Nr.")
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s" % (str)
            part = "%s %s" % (noName[-1], "Nr.")
            return (part, str)
        return None

    def RemoveLetter(self, fromNumber):
        # maybe it contains letter
        m = re.search('[a-zA-Z]', fromNumber)
        if (m is not None):
            group = m.group()
            letterFrom = group
            fromNumber = fromNumber.replace(group, "")
        return fromNumber


    def ExpandStreet(self, street):
        """ yield a tuple(street, house numbe) for each house number found in street """


        print "street %s" % street


        if (street == "" or street == None):
            yield ExpandedStreet(street = "")
            return

        street = street.strip()
        # if no street nr, return single tuple
        if (street.find("Nr") < 0):
            yield ExpandedStreet(street = street)
            return

        parts = street.split(';')

        #print "expand: %s"  % street
        for part in parts:
            streetTuple = self._RemoveStreetPart(part, "g.")
            if (streetTuple is None):
                streetTuple = self._RemoveStreetPart(part, "a.")
            if (streetTuple is None):
                streetTuple = self._RemoveStreetPart(part, "pr.")
            if (streetTuple is None):
                streetTuple = self._RemoveStreetPart(part, "pl.")
            if (streetTuple is None):
                streetTuple = self._RemoveStreetPart(part, "al.")
            if (streetTuple is None):
                streetTuple = self._RemoveStreetPartSB(part, "SB")


            if (streetTuple is not None):
                part, str = streetTuple

            if (part.find('nuo') >= 0):
                noName = part.replace("Nr.", "").replace("numeriai", "").replace("nuo", "").strip()

                # None means that range contains both odd and even numbers
                # True means that contains either of them
                oddNumbers = None
                if (noName.find('poriniai') >= 0):
                    noName = noName.replace("neporiniai", "")
                    noName = noName.replace("poriniai", "")
                    oddNumbers = True

                letterTo = None
                letterFrom = None
                noName = noName.strip()
                noName = noName.split('iki')

                # parse fromNumber
                fromNumber = noName[0].strip()
                fromNumber = self.RemoveLetter(fromNumber)
                fromNumber = int(fromNumber)


                # parse toNumber
                toNumber = noName[1].strip().strip('.')
                if (toNumber == "galo"):
                    odd = fromNumber % 2
                    if (odd == 0):
                        toNumber = ExpandedStreet.MaxEvenValue
                    else:
                        toNumber = ExpandedStreet.MaxOddValue
                else:
                    # maybe it contains letter
                    toNumber = self.RemoveLetter(toNumber)
                    toNumber = int(toNumber)

                if (fromNumber == toNumber):
                    yield ExpandedStreet(str, fromNumber)
                    continue

                if (oddNumbers is None):
                    odd = fromNumber % 2

                    if (odd == 1):
                        oddLow = fromNumber
                        evenLow = fromNumber + 1
                    else:
                        oddLow = fromNumber + 1
                        evenLow = fromNumber

                    odd = toNumber % 2
                    if (odd == 1):
                        oddHigh = toNumber
                        evenHigh = toNumber - 1
                    else:
                        oddHigh = toNumber - 1
                        evenHigh = toNumber

                    yield ExpandedStreet(str, oddLow, oddHigh)
                    yield ExpandedStreet(str, evenLow, evenHigh)
                else:
                    yield ExpandedStreet(str, fromNumber, toNumber)

                #for x in range(fromNumber, toNumber + 1, step):
                #    yield (str, "%s" % x)
#                if (letterTo is not None):
#                    yield (str, "%s%s" % (toNumber, letterTo))
#                if (letterFrom is not None):
#                    yield (str, "%s%s" % (fromNumber, letterFrom))

            elif part.find('Nr.') >= 0:

                noName = part.replace("Nr.", "")
                noName = noName.strip(" .")
                noName = self.RemoveLetter(noName)
                if (noName.find("uo  39 iki  57") >= 0):
                    a = 5
                noName = int(noName)

                yield ExpandedStreet(street = str, numberFrom = noName)




#        streets = street.split("g.")
#        str = streets[0].strip()
#        str = "%s g." % str
#        nrs = streets[1].split("Nr.")
#        for nr in nrs:
#            nr = nr.replace(";", "")
#            nr = nr.strip()
#            if (nr == ""):
#                continue
#            yield (str, nr)



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
            strings.append(" ")
            strings.append(s)


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
