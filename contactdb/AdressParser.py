
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
            yield split[0].strip()
            for semicolonStr in split[1:]:
                self.PushNextCity()
                yield semicolonStr.strip()
            
    def PopCity(self, last = False):
        if last == True:
            return self.popCity

        if (self.pushCity is None):
            return
        if (self.popCity is None):
            return
        returnCity = self.popCity
        self.popCity = self.pushCity
        self.pushCity = None
        return returnCity

    def PushNextCity(self):
        """ a lame way to tell that next city will be a new city, and should not be added to previous"""
        self.forceNextCity = True

    def PushCity(self, city):
        """ a very lame state machine.
        If it find a new street with name "Nr" only, then it does not count it as new street,
        but adds it to the previous street name """

        if (self.pushCity is None):
            self.pushCity = city
            return

        # only if we do not request specifically a new city, try to append current city to existing
        if (self.forceNextCity == False):
            # new city is simply another house number in the same street, so append it and return nothing
            if (city.streetName.lower().find("nr") >= 0):
                self.pushCity.streetName += ", " + city.streetName
                return

        # remove flag just before creating new city
        if (self.forceNextCity == True):
            self.forceNextCity = False;

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

            city = self.PopCity()
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
        
