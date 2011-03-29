#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

import csv
import os
import re
from cdb_lt.management.commands.importSources import ltGeoDataSources_Institution
from cdb_lt.seniunaitijaTerritoryReader import ExpandedStreet
from contactdb.importUtils import getInstitutionNameFromColumn, EnsureExists
from pjutils.exc import ChainnedException

import logging
from territories.houseNumberUtils import ifHouseNumberContainLetter, padHouseNumberWithZeroes, isHouseNumberOdd, removeLetterFromHouseNumber
from territories.ltPrefixes import changeCityFromShortToLongForm, changeStreetFromShortToLongForm, shortStreetEndings

logger = logging.getLogger(__name__)

municipalities = {
        u"Akmenės rajonas":u"Akmenės rajono savivaldybė",
        u"Alytaus miestas":u"Alytaus miesto savivaldybė",
        u"Alytaus rajonas":u"Alytaus rajono savivaldybė",
        u"Anykščių rajonas":u"Anykščių rajono savivaldybė",
        u"BirštonAS":u"Birštono savivaldybė",
        u"Biržų rajonas":u"Biržų rajono savivaldybė",
        u"Druskininkų miestas":u"Druskininkų savivaldybė",
        u"Elektrėnai":u"Elektrėnų savivaldybė",
        u"Ignalinos rajonas":u"Ignalinos rajono savivaldybė",
        u"Jonavos rajonas":u"Jonavos rajono savivaldybė",
        u"Joniškio rajonas":u"Joniškio rajono savivaldybė",
        u"Jurbarko rajonas":u"Jurbarko rajono savivaldybė",
        u"Kaišiadorių rajonas":u"Kaišiadorių rajono savivaldybė",
        u"Kalvarija":u"Kalvarijos savivaldybė",
        u"Kauno miestas":u"Kauno miesto savivaldybė",
        u"Kauno rajonas":u"Kauno rajono savivaldybė",
        u"Kazlų RūdA":u"Kazlų Rūdos savivaldybė",
        u"Kelmės rajonas":u"Kelmės rajono savivaldybė",
        u"Klaipėdos miestas":u"Klaipėdos miesto savivaldybė",
        u"Klaipėdos rajonas":u"Klaipėdos rajono savivaldybė",
        u"Kretingos rajonas":u"Kretingos rajono savivaldybė",
        u"Kupiškio rajonas":u"Kupiškio rajono savivaldybė",
        u"Kėdainių rajonas":u"Kėdainių rajono savivaldybė",
        u"Lazdijų rajonas":u"Lazdijų rajono savivaldybė",
        u"Marijampolės miestas":u"Marijampolės savivaldybė",
        u"Mažeikių rajonas":u"Mažeikių rajono savivaldybė",
        u"Molėtų rajonas":u"Molėtų rajono savivaldybė",
        u"NeringA":u"Neringos savivaldybė",
        u"PagėgIAI":u"Pagėgių savivaldybė",
        u"Pakruojo rajonas":u"Pakruojo rajono savivaldybė",
        u"Palangos miestas":u"Palangos miesto savivaldybė",
        u"Panevėžio miestas":u"Panevėžio miesto savivaldybė",
        u"Panevėžio rajonas":u"Panevėžio rajono savivaldybė",
        u"Pasvalio rajonas":u"Pasvalio rajono savivaldybė",
        u"Plungės rajonas":u"Plungės rajono savivaldybė",
        u"Prienų rajonas":u"Prienų rajono savivaldybė",
        u"Radviliškio rajonas":u"Radviliškio rajono savivaldybė",
        u"Raseinių rajonas":u"Raseinių rajono savivaldybė",
        u"RietavAS":u"Rietavo savivaldybė",
        u"Rokiškio rajonas":u"Rokiškio rajono savivaldybė",
        u"Skuodo rajonas":u"Skuodo rajono savivaldybė",
        u"Tauragės rajonas":u"Tauragės rajono savivaldybė",
        u"Telšių rajonas":u"Telšių rajono savivaldybė",
        u"Trakų rajonas":u"Trakų rajono savivaldybė",
        u"Ukmergės rajonas":u"Ukmergės rajono savivaldybė",
        u"Utenos rajonas":u"Utenos rajono savivaldybė",
        u"Varėnos rajonas":u"Varėnos rajono savivaldybė",
        u"Vilkaviškio rajonas":u"Vilkaviškio rajono savivaldybė",
        u"Vilniaus miestas":u"Vilniaus miesto savivaldybė",
        u"Vilniaus rajonas":u"Vilniaus rajono savivaldybė",
        u"VisaginAS":u"Visagino savivaldybė",
        u"Zarasų rajonas":u"Zarasų rajono savivaldybė",
        u"Šakių rajonas":u"Šakių rajono savivaldybė",
        u"Šalčininkų rajonas":u"Šalčininkų rajono savivaldybė",
        u"Šiaulių miestas":u"Šiaulių miesto savivaldybė",
        u"Šiaulių rajonas":u"Šiaulių rajono savivaldybė",
        u"Šilalės rajonas":u"Šilalės rajono savivaldybė",
        u"Šilutės rajonas":u"Šilutės rajono savivaldybė",
        u"Širvintų rajonas":u"Širvintų rajono savivaldybė",
        u"Švenčionių rajonas":u"Švenčionių rajono savivaldybė"}

def changeMunicipalityToCorrectForm(municipality):
    if not municipalities.has_key(municipality):
        raise ImportStreetsConstituencyDoesNotExist(message="municipality '%s' was not found in standard municipality form list" % municipality)
    return municipalities[municipality]

def changeToGenitiveCityName(city):
    cities = {
        u"Akmenė":u"Akmenės miestas",
        u"Alytus":u"Alytaus miestas",
        u"Anykščiai":u"Anykščių miestas",
        u"Ariogala":u"Ariogalos miestas",
        u"Baltoji Vokė":u"Baltosios Vokės miestas",
        u"Birštonas":u"Birštono miestas",
        u"Biržai":u"Biržų miestas",
        u"Daugai":u"Daugų miestas",
        u"Didieji Gulbinai":u"Didžiųjų Gulbinų kaimas",
        u"Druskininkai":u"Druskininkų miestas",
        u"Dusetos":u"Dusetų miestas",
        u"Dūkštas":u"Dūkšto miestas",
        u"Eišiškės":u"Eišiškių miestas",
        u"Elektrėnai":u"Elektrėnų miestas",
        u"Ežerėlis":u"Ežerėlio miestas",
        u"Galgiai":u"Galgių kaimas",
        u"Gargždai":u"Gargždų miestas",
        u"Garliava":u"Garliavos miestas",
        u"Gelgaudiškis":u"Gelgaudiškio miestelis",
        u"Grigiškės":u"Grigiškių miestas",
        u"Ignalina":u"Ignalinos miestas",
        u"Jieznas":u"Jiezno miestas",
        u"Jonava":u"Jonavos miestas",
        u"Joniškis":u"Joniškio miestas",
        u"Joniškėlis":u"Joniškėlio miestas",
        u"Jurbarkas":u"Jurbarko miestas",
        u"Kaišiadorys":u"Kaišiadorių miestas",
        u"Kalvarija":u"Kalvarijos miestas",
        u"Kaunas":u"Kauno miestas",
        u"Kavarskas":u"Kavarsko miestas",
        u"Kazlų Rūda":u"Kazlų Rūdos miestas",
        u"Kačerginė":u"Kačerginės miestelis",
        u"Kelmė":u"Kelmės miestas",
        u"Klaipėda":u"Klaipėdos miestas",
        u"Kretinga":u"Kretingos smiestas",
        u"Kudirkos Naumiestis":u"Kudirkos Naumiesčio miestas",
        u"Kupiškis":u"Kupiškio miestas",
        u"Kuršėnai":u"Kuršėnų miestas",
        u"Kybartai":u"Kybartų miestas",
        u"Kėdainiai":u"Kėdainių miestas",
        u"Lazdijai":u"Lazdijų miestas",
        u"Lentvaris":u"Lentvario miestas",
        u"Linkuva":u"Linkuvos miestas",
        u"Marijampolė":u"Marijampolės miestas",
        u"Mažeikiai":u"Mažeikių miestas",
        u"Molėtai":u"Molėtų miestas",
        u"Naujoji Akmenė":u"Naujosios Akmenės miestas",
        u"Nemenčinė":u"Nemenčinės miestas",
        u"Neringa":u"Neringos miestas",
        u"Obeliai":u"Obelių miestas",
        u"Pabradė":u"Pabradės miestas",
        u"Pagėgiai":u"Pagėgių miestas",
        u"Pakruojis":u"Pakruojo miestas",
        u"Palanga":u"Palangos miestas",
        u"Pandėlys":u"Pandėlio miestas",
        u"Panemunė":u"Panemunės miestas",
        u"Panevėžys":u"Panevėžio miestas",
        u"Pasvalys":u"Pasvalio miestas",
        u"Plungė":u"Plungės miestas",
        u"Priekulė":u"Priekulės miestas",
        u"Prienai":u"Prienų miestas",
        u"Radviliškis":u"Radviliškio miestas",
        u"Raseiniai":u"Raseinių miestas",
        u"Rietavas":u"Rietavo miestas",
        u"Rokiškis":u"Rokiškio miestas",
        u"Rusnė":u"Rusnės miestelis",
        u"Rūdiškės":u"Rūdiškių miestas",
        u"Simnas":u"Simno miestas",
        u"Skaudvilė":u"Skaudvilės miestas",
        u"Skuodas":u"Skuodo miestas",
        u"Smalininkai":u"Smalininkų miestas",
        u"Tauragė":u"Tauragės miestas",
        u"Telšiai":u"Telšių miestas",
        u"Trakai":u"Trakų miestas",
        u"Troškūnai":u"Troškūnų miestas",
        u"Tyruliai":u"Tyrulių miestelis",
        u"Tytuvėnai":u"Tytuvėnų miestas",
        u"Ukmergė":u"Ukmergės miestas",
        u"Utena":u"Utenos miestas",
        u"Užventis":u"Užvenčio miestas",
        u"Vabalninkas":u"Vabalninko miestas",
        u"Varniai":u"Varnių miestas",
        u"Varėna":u"Varėnos miestas",
        u"Veisiejai":u"Veisiejų miestas",
        u"Venta":u"Ventos miestas",
        u"Viekšniai":u"Viekšnių miestas",
        u"Vievis":u"Vievio miestas",
        u"Vilkaviškis":u"Vilkaviškio miestas",
        u"Vilkija":u"Vilkijos miestas",
        u"Vilnius":u"Vilniaus miestas",
        u"Virbalis":u"Virbalio miestas",
        u"Visaginas":u"Visagino miestas",
        u"Zarasai":u"Zarasų miestas",
        u"Šakiai":u"Šakių miestas",
        u"Šalčininkai":u"Šalčininkų miestas",
        u"Šeduva":u"Šeduvos miestas",
        u"Šiauliai":u"Šiaulių miestas",
        u"Šilalė":u"Šilalės miestas",
        u"Šilutė":u"Šilutės miestas",
        u"Širvintos":u"Širvintų miestas",
        u"Švenčionys":u"Švenčionių miestas",
        u"Švenčionėliai":u"Švenčionėlių miestas",
        u"Žagarė":u"Žagarės miestas",
        u"Žemaičių Naumiestis":u"Žemaičių Naumiesčio miestelis",
        u"Žiežmariai":u"Žiežmarių miestas",
    }
    if not cities.has_key(city) :
        return city

    newcity = cities[city]
    #print "substituting %s to %s" %(city, newcity)
    return newcity

class CityStreet:
    cityName = ""
    streetName = ""

    def __init__(self, cityName = "", streetName = ""):

        # convert short city ending to long city ending
        self.cityName = changeCityFromShortToLongForm(cityName)
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
        if re.search("\sg\.", street) is not None:
            return True
        if re.search("SB\s", street, flags = re.IGNORECASE) is not None:
            return True
        if re.search("\spr\.", street) is not None:
            return True
        if re.search("\spl\.", street) is not None:
            return True
        if re.search("\sa\.", street) is not None:
            return True
        if re.search("\sal\.", street) is not None:
            return True
        return False

    def _getStreets(self, streetStr):
        streets = streetStr.split(",")
        # split by comma, we get either cities, or streets
        for s in streets:
            # a village is separate by its first street by a colon
            s = s.strip()
            if s.find(";") < 0:
                yield s
                continue
            split = s.split(";")

            # if it contains a "g.", short for "street" int Lithuanian, then this will be new street, so push new one
            if self._containsOneOfStreets(split[0]):
                self.PushSemicolonCity()

            yield split[0].strip()
            for semicolonStr in split[1:]:
                semicolonStr = semicolonStr.strip()
                if semicolonStr == "":
                    continue

                # if it contains a "g.", short for "street" int Lithuanian, then this will be new street, so push new one
                if self._containsOneOfStreets(semicolonStr) > 0:
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

        if self.pushCity is None:
            return
        if self.popCity is None:
            return
        if self.shouldAdd(str) == True:
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
        if self.forceNextSemicolonCity == True:
            return False

        if streetName.find("poriniai") >= 0:
            return True
        if streetName.find("numeriai nuo") >= 0:
            return True
        return False

    def __shouldAddNr(self, streetName):
        streetName = streetName.lower()
        # only if we do not request specifically a new city, try to append current city to existing
        if self.forceNextCity == False:
            # new city is simply another house number in the same street, so append it and return nothing
            if streetName.find("nr") >= 0:
                return True
        return False

    def shouldAdd(self, streetName):
        """ given a steetName, tells if this should be added to current city, or to the new one"""
        streetName = streetName.lower()

        if self._containsOneOfStreets(streetName):
            return False;

        # if either of force flag is set, return false
        if self.forceNextSemicolonCity == True:
            return False

        if self.__shouldAddPoriniai(streetName) == True:
            return True
        if self.__shouldAddNr(streetName) == True:
            return True
        return False

    def removeForceFlags(self):
        self.forceNextCity = False
        self.forceNextSemicolonCity = False

    def _addStreetNameToCurrentCity(self, city):
        if self.pushCity is not None:
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
        if city.streetName.startswith("nuo") == True:
            self._addStreetNameToCurrentCity(city)
            return

        if self.pushCity is None:
            self.pushCity = city
            self.removeForceFlags()
            return



        # poriniai / neporiniai / numeriai nuo types of addresses ignore forceNextCity control
        # these constructs must always come together
        if self.__shouldAddPoriniai(city.streetName):
            self.pushCity.streetName += "; " + city.streetName
            return

        # only if we do not request specifically a new city, try to append current city to existing
        if self.__shouldAddNr(city.streetName):
            self.pushCity.streetName += "; " + city.streetName
            return

        # remove flag just before creating new city
        self.removeForceFlags()

        self.popCity = self.pushCity
        self.pushCity = city



    def restart(self):
        self.pushCity = None
        self.popCity = None
        self.forceNextCity = False

    def GetAddresses(self, addressStr):
        self.restart()
        cityName = ""



        for str in self._getStreets(addressStr):

            city = self.PopCity(str)
            if city is not None:
                yield city

            # colon tests is this a village. After a village name, follows a colon and then
            # a list of streets belonging to that village.
            # test for colon must come first, before village testing (otherwise tests fail)
            if str.find(":") >= 0:
                splitStr = str.split(":")
                cityName = splitStr[0].strip()
                c = CityStreet(cityName, splitStr[1].strip())
                self.PushCity(c)
                continue

            # "mstl" stand for small town in Lithuanian
            if str.find("mstl") >= 0:
                c = CityStreet(str, "")
                self.PushCity(c)
                continue

            # "k." stands for village, or kaimas in Lithuanian.
            #if (str.find("k.") >= 0):
            if re.search("\sk\.", str) is not None:
                c = CityStreet(str, "")
                self.PushCity(c)
                continue

            c = CityStreet(cityName, str)
            self.PushCity(c)
        if self.popCity is not None:
            yield self.popCity
        if self.pushCity is not None:
            yield self.pushCity


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
    # rajonas
    District = ""
    # apygarda
    Constituency = None
    # apylinkė
    PollingDistrict = ""
    Addresses = ""
    pollingDistrictAddress = None
    numberOfVoters = None


class Constituency(object):
    def __init__(self):
        name = u""
        nr = 0

class NotFoundConstituencyNrException(ChainnedException):
    pass

class LithuanianConstituencyParser:

    def ExtractConstituencyFromMPsFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian MPs file """
        lower = constituencyString.lower().strip()
        if lower == "":
            return None

        # išrinktas pagal sąrašą means that MP does not have a constituency
        if lower.find(u"pagal sąrašą") > 0:
            return None
        nr = lower.find("nr")
        if nr < 0:
            raise NotFoundConstituencyNrException(u"Could not parse Constituency nr in string '%(s)s'" % {"s" : lower})
        c = Constituency()
        c.name = constituencyString[:nr].strip(" (")
        c.nr =  int(constituencyString[nr + 3: ].strip(" )"))
        return c

    def ExtractConstituencyFromConstituencyFile(self, constituencyString):
        """Extracts a Constituency object from a Lithuanian Constituency file"""
        lower =  constituencyString.lower()
        nr = lower.find("nr")
        if nr < 0:
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
            if s == u"":
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
            if s == u"":
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
        while True:
            line = self._notEmptyLine()

            if line == u"":
                return

            if line.find(u"apygarda") >=0 :
                location.Constituency = self.constituencyParser.ExtractConstituencyFromConstituencyFile(line)
                state = State.PollingDistrict
                continue

            if line.find(u"apylink") >=0:
                location.PollingDistrict = line
                state = State.Addresses

                #if (line.find("S. Daukanto rinkimų apylinkė Nr. 64") >= 0):
                #    print state

                # this Constituency is special, since it has no streets.
                # So just instruct so skip reading streets for this Constituency
                # HACK for now, but works
                # If you remove it, a test will fail
                if line.find(u"Jūreivių rinkimų apylinkė") >=0 :
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
        if part.find(streetPartName) >= 0:
            noName = part.split(streetPartName)
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s %s" % (str, streetPartName)
            part = noName[-1]
            return (part, str)
        return None

    def _RemoveStreetPartSB(self, part, streetPartName):
        if part.find(streetPartName) >= 0:
            noName = part.split("Nr.")
            noName = [s.strip() for s in noName]
            str = "".join(noName[0:-1])
            str = "%s" % (str)
            part = "%s %s" % (noName[-1], "Nr.")
            return (part, str)
        return None

    def getStreetTuple(self, part):
        streetTuple = None
        # loop all street endings and remove it if found
        for ending in shortStreetEndings:
            if streetTuple is not None:
                break
            streetTuple = self._RemoveStreetPart(part, ending)

        # if it is still None, there is a special "SB", which stands for
        # "Some kind of communal gardens, or smth like that"
        if streetTuple is None:
            streetTuple = self._RemoveStreetPartSB(part, "SB")
        return streetTuple

    def ExpandStreet(self, street):
        """ yield a ExpandedStreet object for each house number found in street """


        #print "street %s" % street


        if street == u"" or street == None:
            yield ExpandedStreet(street = u"")
            return

        street = street.strip()
        # if no street nr, return single tuple
        if street.find(u"Nr") < 0:
            street = changeStreetFromShortToLongForm(street)
            yield ExpandedStreet(street = street)
            return

        parts = street.split(u';')

        # rembember if previous number was even/odd, or both (i.e. None)
        previousNumberOdd = None

        for part in parts:
            streetTuple = self.getStreetTuple(part)

            if streetTuple is not None:
                part, str = streetTuple
                # street will be in short form, so transform it to be in long form
                str = changeStreetFromShortToLongForm(str)

            if part.find(u'nuo') >= 0:
                noName = part.replace(u"Nr.", u"").replace(u"numeriai", u"").replace(u"nuo", u"").strip()

                # None means that range contains both odd and even numbers
                # True means that contains either of them
                oddNumbers = None
                if noName.find(u'poriniai') >= 0:
                    noName = noName.replace(u"neporiniai", u"")
                    noName = noName.replace(u"poriniai", u"")
                    oddNumbers = True
                    previousNumberOdd = True

                # if current range does not define whether we are even or odd, check what previous range was
                if oddNumbers == None:
                    oddNumbers = previousNumberOdd

                noName = noName.strip()
                noName = noName.split(u'iki')

                # parse fromNumber
                fromNumber = noName[0].strip()
                if ifHouseNumberContainLetter(fromNumber):
                    yield ExpandedStreet(str, fromNumber)
                    fromNumber = removeLetterFromHouseNumber(fromNumber)
                    fromNumber = int(fromNumber) + 2
                else:
                    fromNumber = int(fromNumber)


                # parse toNumber
                toNumber = noName[1].strip().strip('.')
                if toNumber == u"galo":
                    odd = fromNumber % 2
                    if (odd == 0):
                        toNumber = ExpandedStreet.MaxEvenValue
                    else:
                        toNumber = ExpandedStreet.MaxOddValue
                else:
                    # maybe it contains letter
                    toNumber = removeLetterFromHouseNumber(toNumber)
                    toNumber = int(toNumber)

                if fromNumber == toNumber:
                    yield ExpandedStreet(str, fromNumber)
                    continue

                yield ExpandedStreet(str, fromNumber, toNumber)

            elif part.find(u'Nr.') >= 0:

                noName = part.replace(u"Nr.", u"")
                noName = noName.strip(u" .")
                noName = noName
                if ifHouseNumberContainLetter(noName) == False:
                    noName = int(noName)

                yield ExpandedStreet(street = str, numberFrom = noName)

class mpStreetReader(object):
    def __init__(self, delimiter=","):
        self.delimiter = delimiter
        self.institutionNameGetter = getInstitutionNameFromColumn
        self.unparsedInstitutions = {}


    def yieldTerritories(self):
        EnsureExists(ltGeoDataSources_Institution.LithuanianMPStreetData)
        allRecords = os.path.join(os.getcwd(), ltGeoDataSources_Institution.LithuanianMPStreetData)
        file = open(allRecords, "r")
        aggregator = LithuanianConstituencyReader(file)


        streetParser = AddressParser()
        streetExpander = PollingDistrictStreetExpander()


        imported = 0


        print u"starting to import streets"
        count = 0
        for pollingDistrict in aggregator.getLocations():
            count += 1
            imported += 1
            for address in streetParser.GetAddresses(pollingDistrict.Addresses):
                expandedStreets = list(streetExpander.ExpandStreet(address.streetName))
                for expandedStreet in expandedStreets:
                    municipality = changeMunicipalityToCorrectForm(pollingDistrict.District)
                    city = changeToGenitiveCityName(address.cityName)

                    expandedStreetStr = expandedStreet.street
                    if expandedStreetStr == u"V. Druskio gatvė":
                        expandedStreetStr = u"Virginijaus Druskio gatvė"
                    street = expandedStreetStr
                    numberFrom =  padHouseNumberWithZeroes(expandedStreet.numberFrom)
                    numberTo = padHouseNumberWithZeroes(expandedStreet.numberTo)
                    if numberFrom is not None:
                       numberOdd = isHouseNumberOdd(expandedStreet.numberFrom)
                    civilParish = u""
                    constit = pollingDistrict.Constituency
                    institutionKey = u"%s Nr. %s" % (constit.name, constit.nr)
                    yield (institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)

