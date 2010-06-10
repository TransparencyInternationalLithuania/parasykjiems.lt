#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianCountyReader

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestAddressParser(TestCase):
    parser = AddressParser()
    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"

    def test_OneCity(self):
        file = open(self.singleRecordFile, "r")
        importer = LithuanianCountyReader(file)
        loc = list(importer.getLocations())[0]

        addressStr = loc.Addresses

        parsed = list(self.parser.GetAddresses(addressStr))

        self.assertEqual("Naujoji Akmenė", parsed[0].cityName)
        self.assertEqual("Algirdo g.", parsed[0].streetName)

        self.assertEqual("Aušros g.", parsed[1].streetName)

        self.assertEqual(55, len(parsed))

        """Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs., Beržyno g.,
Botanikos sodas „Puošmena“, Čiapo vs., Dambrausko vs., Darbininkų g.,
Eibučių g., Gedimino g., Gintausko vs., Guginio vs., J. Dalinkevičiaus"""
        





