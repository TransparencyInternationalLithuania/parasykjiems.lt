
class CityStreet:
    cityName = ""
    streetName = ""

    def __init__(self, cityName = "", streetName = ""):
        self.cityName = cityName
        self.streetName = streetName
        pass


class AddressParser:

    def _getStreets(self, streetStr):
        streets = streetStr.split(",")
        # split by comma, we get either cities, or streets
        for s in streets:
            # a village is separate by its first street by a colon
            for s1 in s.split(";"):
                yield s1.strip()

    def GetAddresses(self, addressStr):

        cityName = ""

        for str in self._getStreets(addressStr):
            if (str.find("k.") > 0):
                c = CityStreet(str, "")
                yield c
                continue

            if (str.find(":") > 0):
                splitStr = str.split(":")
                cityName = splitStr[0].strip()
                c = CityStreet(cityName, splitStr[1].strip())
                yield c
                continue

            c = CityStreet(cityName, str)
            yield c
