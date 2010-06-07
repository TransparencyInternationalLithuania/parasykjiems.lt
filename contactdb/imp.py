#!/usr/bin/env python
# -*- coding: utf8 -*-

import copy
import contactdb.tests.exc
from contactdb.tests.exc import ChainnedException
from contactdb.models import County

municipalities = "sources/apygardos.txt"



class ImportSources:
    LithuanianCounties = "/contactdb/sources/apygardos.txt"




# simply introducing an enumartion, so that we can use
# this as states when reading file.
# Probably might be a better way to do this in python
class State:
    # values here does not mean anything at all
    District = "d"
    County = "c"
    ElectionDistrict = "ec"
    Addresses = "ad"


# a DTO which is returned for eaach location read in the file
class MunicipalityLocation:
    District = ""
    County = None
    ElectionDistrict = ""
    Addresses = ""

    # how to convert python object to string?
    # dont know yet, so using this hack :)
    # we could also iterate over all "fields??" in this object
    # but how to do that??
    def __str__(self):
        return "District: " + self.District + "\nCounty " + self.County + "\nElectionDistrict " + self.ElectionDistrict + "\nAddresses " + self.Addresses


class LithuanianCountyAggregator:
    """ Aggregates MunicipalityLocation objects and returns only unique Counties"""
    def __init__(self, file):
        self.file = file
        self.importer = LithuanianCountyReader(file)
        self.allCounties = []

        self._readAll()

    def _readAll(self):
        for loc in self.importer.getLocations():
            self.allCounties.append(loc)

    def GetDistinctCounties(self):
        """
        Returns a list of string for each distinct County
        """
        counties = {}
                           
        for c in self.allCounties:
            exist = c.County in counties
            if (exist == False):
                counties[c.County] = c
                yield c.County
            
        
        

class NotFoundCountyNrException(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)

class LithuanianCountyParser:
    def ConvertToCounty(self, countyString):
        lower = countyString.lower()
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundCountyNrException("Could not parse county nr in string '%(string)s'") % {"string" : lower}
        c = County()
        c.name = countyString[:nr].strip(" ")
        c.nr =  int(countyString[nr + 3: ])
        return c


class LithuanianCountyReader:
    """ Reads Lithuanian counties from file. Gives a generator function
    which returns a single MunicipalityLocation instance for each smallest object
    defined in file( ElectionDistrict/ (rinkimų apylinkė)
    """
    def __init__(self, file):
        """Pass an opened file containing Lithuanian Counties (Apygardos)."""
        self.file = file
        self.countyParser = LithuanianCountyParser()


    def _ConsumeNonEmptyLines(self, numberOfLines):
        for i in range(1, numberOfLines):
            self._notEmptyLine()

    # a function which returns only non empty
    # lines specific for Lithuanian municipality files.
    def _notEmptyLine(self):

        # read a line from file
        for s in self.file:

            # return each splitted line as separate line
            s = self._removeDumbCharacters(s)
            if (s == ""):
                continue
            return s

        return ""

    def _removeDumbCharacters(self, str):
        return str.strip("* \n")

    def _readAddress(self):
        strings = []
        # read first non empty line. This ensures that all blank lines are skipped
        strings.append(self._notEmptyLine())

        # read all non empty lines, and append to list
        # when empty strins is found, that means addresses are finished
        for s in self.file:
            s = self._removeDumbCharacters(s)
            if (s == ""):
                break;
            strings.append(s)

        return "".join(strings)

    # a generator which returns a MunicipalityLocation object
    # for each election district defined in the file
    def getLocations(self):
        state = State.District
        location = MunicipalityLocation()
        while (1):
            line = self._notEmptyLine()

            if (line == ""):
                return

            if (line.find("apygarda") >=0 ):
                location.County = self.countyParser.ConvertToCounty(line)
                state = State.ElectionDistrict
                continue

            if (line.find("apylink") >=0 ):
                location.ElectionDistrict = line
                state = State.Addresses

                # this county is special, since it has no streets.
                # So just instruct so skip reading streets for this county
                # HACK for now, but works
                # If you remove it, a test will fail
                if (line.find("Jūreivių rinkimų apylinkė") >=0 ):
                    yield location
                    state = State.County

                self._ConsumeNonEmptyLines(2)
                continue

            if state == State.District:
                location.District = line
                state = State.County
                continue

            if (state == State.Addresses):
                location.Addresses = self._readAddress()
                state = State.District
                clone = copy.copy(location)
                yield clone



"""
# debugging script, remove afterwards

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )
alytusRecordFile = scriptPath + "/tests/AlytausMiestas.txt"
print alytusRecordFile

def countNumberOfRecords(fileName):
        file = open(fileName, "r")
        count = 0
        for l in getLocations(file):
            print l.ElectionDistrict
            count += 1
        return count


print countNumberOfRecords(alytusRecordFile)
"""