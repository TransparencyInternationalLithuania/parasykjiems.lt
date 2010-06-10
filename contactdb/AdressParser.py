
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
        for s in streets:
            yield s.strip()

    def GetAddresses(self, addressStr):
        cities = addressStr.split(":")

        count = 0
        # do not now how to loop normally, so i introduce
        # a fake variable a, and use count instead
        for a in cities:
            if (count >= len(cities) / 2):
                break
            city = cities[count]
            streets = cities[count + 1]

            for street in self._getStreets(streets):
                contact = CityStreet(city, street)
                yield contact

            count += 1
