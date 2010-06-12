
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
        if (street.find("g.") > 0):
            return True
        if (street.find("pr.") > 0):
            return True
        if (street.find("pl.") > 0):
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

    def PushCity(self, city):
        """ a very lame state machine.
        If it find a new street with name "Nr" only, then it does not count it as new street,
        but adds it to the previous street name """

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
            if (str.find(":") > 0):
                splitStr = str.split(":")
                cityName = splitStr[0].strip()
                c = CityStreet(cityName, splitStr[1].strip())
                self.PushCity(c)
                continue

            # "mstl" stand for small town in Lithuanian
            if (str.find("mstl") > 0):
                c = CityStreet(str, "")
                self.PushCity(c)
                continue
                
            # "k." stands for village, or kaimas in Lithuanian. 
            if (str.find("k.") > 0):
                c = CityStreet(str, "")
                self.PushCity(c)
                continue

            c = CityStreet(cityName, str)
            self.PushCity(c)
        if (self.popCity is not None):
            yield self.popCity
        if (self.pushCity is not None):
            yield self.pushCity
        
