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

    def assertCity(self, cityName, streetName, cityAddress):
        self.assertEqual(cityName, cityAddress.cityName)
        self.assertEqual(streetName, cityAddress.streetName)


    def test_TwoCities(self):
        streetStr = "Gajauciškio k., Gemaitiškių k., Jurkionių k.: SB „Dzūkija“, Medukštos k., Navasiolkų k., Norgeliškių k., Padvariškių k., Panemuninkėlių k.; Panemuninkų k.: SB „Versmė“; Raganiškių k., Strielčių k., Taučionių k., Vaidaugų k., Vaisodžių k., Vaišupio k., Valiūnų k., Žiūkų k."

    def test_Villages_And_OneCity(self):
        streetStr = "Bažavos k., Kolonistų k.; Simnas: Alytaus g., Ateities g., Birutės g., Dariaus ir Girėno g., Draugystės g., Ežero g., Jaunimo g., Kaimynų g., Kreivoji g., Laisvės g., Melioratorių g., Naujoji g., Paupio g., Pavasario g., S. Nėries g., Saulėtekio g., Šviesos g., Taikos g., Vanagėlio g., Vytauto g., Žalioji g., Žemaitės g."

        parsed = list(self.parser.GetAddresses(streetStr))
        bazavos = parsed[0]
        kolonistu = parsed[1]
        simnasAlytaus = parsed[2]
        simnasAteities = parsed[3]
        simnasBirutes = parsed[4]
        self.assertCity("Bažavos k.", "", bazavos)
        self.assertCity("Kolonistų k.", "", kolonistu)
        self.assertCity("Simnas", "Alytaus g.", simnasAlytaus)
        self.assertCity("Simnas", "Ateities g.", simnasAteities)
        self.assertCity("Simnas", "Birutės g.", simnasBirutes)


    def test_OneCity_ManyStreets(self):
        file = open(self.singleRecordFile, "r")
        importer = LithuanianCountyReader(file)
        loc = list(importer.getLocations())[0]

        addressStr = loc.Addresses

        parsed = list(self.parser.GetAddresses(addressStr))

        self.assertCity("Naujoji Akmenė", "Algirdo g.", parsed[0])

        self.assertCity("Naujoji Akmenė", "Aušros g.", parsed[1])

        self.assertEqual(55, len(parsed))

        """Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs., Beržyno g.,
Botanikos sodas „Puošmena“, Čiapo vs., Dambrausko vs., Darbininkų g.,
Eibučių g., Gedimino g., Gintausko vs., Guginio vs., J. Dalinkevičiaus"""
        





