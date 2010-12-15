#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from pjutils.exc import ChainnedException
from cdb_lt_mps.models import Constituency
from pjutils.deprecated import deprecated
import copy


class CityStreet:
    cityName = ""
    streetName = ""

    def __init__(self, cityName = "", streetName = ""):
        self.cityName = cityName
        self.streetName = streetName
        pass


class AddressParser:

    pushCity = None
    popCity = None
    forceNextCity = False
    forceNextSemicolonCity = False

    def _containsOneOfStreets(self, street):
        """returns True if street name contains a lithuanian shortened form of street: g for garve,
        pl for plentas, pr for prospektas, etc"""
        if (re.search("\sg\.", street) is not None):
            return True
        if (re.search("SB\s", street, flags = re.IGNORECASE) is not None):
            return True
        if (re.search("\spr\.", street) is not None):
            return True
        if (re.search("\spl\.", street) is not None):
            return True
        if (re.search("\sa\.", street) is not None):
            return True
        if (re.search("\sal\.", street) is not None):
            return True
        return False

    def _getStreets(self, streetStr):
        streets = streetStr.split(",")
        # split by comma, we get either cities, or streets
        for s in streets:
            # a village is separate by its first street by a colon
            s = s.strip()
            if (s.find(";") < 0):
                yield s
                continue
            split = s.split(";")

            # if it contains a "g.", short for "street" int Lithuanian, then this will be new street, so push new one
            if (self._containsOneOfStreets(split[0])):
                self.PushSemicolonCity()

            yield split[0].strip()
            for semicolonStr in split[1:]:
                semicolonStr = semicolonStr.strip()
                if (semicolonStr == ""):
                    continue

                # if it contains a "g.", short for "street" int Lithuanian, then this will be new street, so push new one
                if (self._containsOneOfStreets(semicolonStr) > 0):
                    self.PushSemicolonCity()

                # every semicolon divides one city from another
                # however, not for the case with "poriniai / neporiniai"
                # for this reason we have to pushCity flags (i.e. PushNextCity and PushSemicolonCity
                self.PushNextCity()
                yield semicolonStr.strip()

    def PushSemicolonCity(self):
        self.forceNextSemicolonCity = True


    def PopCity(self, str ="", last = False):
        if last == True:
            return self.popCity

        if (self.pushCity is None):
            return
        if (self.popCity is None):
            return
        if (self.shouldAdd(str) == True):
            return
        returnCity = self.popCity
        self.popCity = self.pushCity
        self.pushCity = None
        return returnCity

    def PushNextCity(self):
        """ a lame way to tell that next city will be a new city, and should not be added to previous"""
        self.forceNextCity = True


    def __shouldAddPoriniai(self, streetName):
        """ Returns true if existing street name should be appended to existing city.
        flag forceNextSemicolonCity forces either to exclude always, or do the checking"""

        # poriniai / neporiniai / numeriai nuo types of addresses ignore forceNextCity control
        # these constructs must always come together
        streetName = streetName.lower()
        if (self.forceNextSemicolonCity == True):
            return False

        if (streetName.find("poriniai") >= 0):
            return True
        if (streetName.find("numeriai nuo") >= 0):
            return True
        return False

    def __shouldAddNr(self, streetName):
        streetName = streetName.lower()
        # only if we do not request specifically a new city, try to append current city to existing
        if (self.forceNextCity == False):
            # new city is simply another house number in the same street, so append it and return nothing
            if (streetName.find("nr") >= 0):
                return True
        return False

    def shouldAdd(self, streetName):
        """ given a steetName, tells if this should be added to current city, or to the new one"""
        streetName = streetName.lower()

        if (self._containsOneOfStreets(streetName)):
            return False;

        # if either of force flag is set, return false
        if (self.forceNextSemicolonCity == True):
            return False

        if (self.__shouldAddPoriniai(streetName) == True):
            return True
        if (self.__shouldAddNr(streetName) == True):
            return True
        return False

    def removeForceFlags(self):
        self.forceNextCity = False
        self.forceNextSemicolonCity = False

    def _addStreetNameToCurrentCity(self, city):
        if (self.pushCity is not None):
            self.pushCity.streetName = "%s; %s" % (self.pushCity.streetName, city.streetName)
            return
        self.popCity.streetName = "%s; %s" % (self.popCity.streetName, city.streetName)


    def PushCity(self, city):
        """ a very lame state machine.
        If it finds a new street with name "Nr" only, then it does not count it as new street,
        but adds it to the previous street name """

        city.streetName = city.streetName.strip()
        #if (city.streetName.find("nuo Nr. 70") >=0 ):
        #    a = 5
        if (city.streetName.startswith("nuo") == True):
            self._addStreetNameToCurrentCity(city)
            return

        if (self.pushCity is None):
            self.pushCity = city
            self.removeForceFlags()
            return



        # poriniai / neporiniai / numeriai nuo types of addresses ignore forceNextCity control
        # these constructs must always come together
        if (self.__shouldAddPoriniai(city.streetName)):
            self.pushCity.streetName += "; " + city.streetName
            return

        # only if we do not request specifically a new city, try to append current city to existing
        if (self.__shouldAddNr(city.streetName)):
            self.pushCity.streetName += "; " + city.streetName
            return

        # remove flag just before creating new city
        self.removeForceFlags()

        self.popCity = self.pushCity
        self.pushCity = city



    def restart(self):
        self.pushCity = None
        self.popCity = None
        self.forceNextCity = False;

    def GetAddresses(self, addressStr):
        self.restart()
        cityName = ""



        for str in self._getStreets(addressStr):

            city = self.PopCity(str)
            if (city is not None):
                yield city

            # colon tests is this a village. After a village name, follows a colon and then
            # a list of streets belonging to that village.
            # test for colon must come first, before village testing (otherwise tests fail)
            if (str.find(":") >= 0):
                splitStr = str.split(":")
                cityName = splitStr[0].strip()
                c = CityStreet(cityName, splitStr[1].strip())
                self.PushCity(c)
                continue

            # "mstl" stand for small town in Lithuanian
            if (str.find("mstl") >= 0):
                c = CityStreet(str, "")
                self.PushCity(c)
                continue

            # "k." stands for village, or kaimas in Lithuanian.
            #if (str.find("k.") >= 0):
            if (re.search("\sk\.", str) is not None):
                c = CityStreet(str, "")
                self.PushCity(c)
                continue

            c = CityStreet(cityName, str)
            self.PushCity(c)
        if (self.popCity is not None):
            yield self.popCity
        if (self.pushCity is not None):
            yield self.pushCity



class PollingDistrictStreetExpanderException(ChainnedException):
    pass

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
        """ yield a ExpandedStreet object for each house number found in street """


        #print "street %s" % street


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
    pass

class LithuanianConstituencyParser:

    def ExtractConstituencyFromMPsFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian MPs file """
        lower = constituencyString.lower().strip()
        if (lower == ""):
            return None

        # išrinktas pagal sąrašą means that MP does not have a constituency
        if (lower.find(u"pagal sąrašą") > 0):
            return None
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundConstituencyNrException(u"Could not parse Constituency nr in string '%(s)s'" % {"s" : lower})
        c = Constituency()
        c.name = constituencyString[:nr].strip(" (")
        c.nr =  int(constituencyString[nr + 3: ].strip(" )"))
        return c

    def ExtractConstituencyFromConstituencyFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian Constituency file"""
        lower =  constituencyString.lower()
        nr = lower.find("nr")
        if (nr < 0):
            raise NotFoundConstituencyNrException(u"Could not parse constituency nr in string '%(string)s'") % {"string" : lower}
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

    # a function which returns only non empty
    # lines specific for Lithuanian municipality files.
    def _notEmptyLine(self):

        # read a line from file
        for s in self.file:
            s = unicode(s, 'utf-8')
            # return each splited line as separate line
            s = self._removeDumbCharacters(s)
            if (s == u""):
                continue
            return s

        return ""

    def _removeDumbCharacters(self, str):
        return str.strip(u"* \r\n")

    def _readAddress(self):
        strings = []
        # read first non empty line. This ensures that all blank lines are skipped
        strings.append(self._notEmptyLine())

        # read all non empty lines, and append to list
        # when empty strings is found, that means addresses are finished
        for s in self.file:
            s = unicode(s, 'utf-8')
            s = self._removeDumbCharacters(s)
            if (s == u""):
                break
            strings.append(u" ")
            strings.append(s)


        return u"".join(strings)

    def readParagraph(self):
        s = ""
        for s in self.file:
            s = unicode(s, 'utf-8')
            s = self._removeDumbCharacters(s)
            if s != u"":
                break

        adr = []
        adr.append(s)
        for s in self.file:
            s = unicode(s, 'utf-8')
            s = self._removeDumbCharacters(s)
            if s == u"":
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

            if (line == u""):
                return

            if (line.find(u"apygarda") >=0 ):
                location.Constituency = self.constituencyParser.ExtractConstituencyFromConstituencyFile(line)
                state = State.PollingDistrict
                continue

            if (line.find(u"apylink") >=0 ):
                location.PollingDistrict = line
                state = State.Addresses

                #if (line.find("S. Daukanto rinkimų apylinkė Nr. 64") >= 0):
                #    print state

                # this Constituency is special, since it has no streets.
                # So just instruct so skip reading streets for this Constituency
                # HACK for now, but works
                # If you remove it, a test will fail
                if (line.find(u"Jūreivių rinkimų apylinkė") >=0 ):
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
