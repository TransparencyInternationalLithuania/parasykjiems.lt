#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianCountyReader

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestAddressParser(TestCase):

    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"

    def setUp(self):
        self.parser = AddressParser()



    def assertCity(self, cityName, streetName, cityAddress):
        self.assertEqual(cityName, cityAddress.cityName)
        self.assertEqual(streetName, cityAddress.streetName)

    def test_Street_WithPoriniai(self):
        streetStr = "Naujoji Akmenė: Respublikos g. Nr. 19, Nr. 26, Nr. 28, numeriai nuo Nr. 1 iki Nr. 17; Respublikos a. Nr. 2."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Naujoji Akmenė", "Respublikos g. Nr. 19, Nr. 26, Nr. 28, numeriai nuo Nr. 1 iki Nr. 17", parsed[0])
        self.assertCity("Naujoji Akmenė", "Respublikos a. Nr. 2.", parsed[1])
        self.assertEqual(2, len(parsed))

    def test_Street_WithHouseNumbers(self):
        streetStr = "Naujoji Akmenė: Respublikos g. Nr. 18, Nr. 20, Nr. 21, Nr. 23, Nr. 24, Nr. 25, Nr. 27; SB „Ąžuolas“, V. Kudirkos g."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Naujoji Akmenė", "Respublikos g. Nr. 18, Nr. 20, Nr. 21, Nr. 23, Nr. 24, Nr. 25, Nr. 27", parsed[0])
        self.assertCity("Naujoji Akmenė", "SB „Ąžuolas“", parsed[1])
        self.assertCity("Naujoji Akmenė", "V. Kudirkos g.", parsed[2])
        self.assertEqual(3, len(parsed))



    def test_TwoCities(self):
        streetStr = "Gajauciškio k., Gemaitiškių k., Jurkionių k.: SB „Dzūkija“, Medukštos k., Navasiolkų k., Norgeliškių k., Padvariškių k., Panemuninkėlių k.; Panemuninkų k.: SB „Versmė“; Raganiškių k., Strielčių k., Taučionių k., Vaidaugų k., Vaisodžių k., Vaišupio k., Valiūnų k., Žiūkų k."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Gajauciškio k.", "", parsed[0])
        self.assertCity("Gemaitiškių k.", "", parsed[1])
        self.assertCity("Jurkionių k.", "SB „Dzūkija“", parsed[2])
        self.assertCity("Medukštos k.", "", parsed[3])
        self.assertCity("Navasiolkų k.", "", parsed[4])
        self.assertCity("Norgeliškių k.", "", parsed[5])
        self.assertCity("Padvariškių k.", "", parsed[6] )
        self.assertCity("Panemuninkėlių k.", "", parsed[7])
        self.assertCity("Panemuninkų k.", "SB „Versmė“", parsed[8])
        self.assertCity("Raganiškių k.", "", parsed[9])
        self.assertCity("Strielčių k.", "", parsed[10])
        self.assertCity("Taučionių k.", "", parsed[11])
        self.assertCity("Vaidaugų k.", "", parsed[12]  )
        self.assertCity("Vaisodžių k.", "", parsed[13]  )
        self.assertCity("Vaišupio k.", "", parsed[14])
        self.assertCity("Valiūnų k.", "", parsed[15])
        self.assertCity("Žiūkų k.", "", parsed[16])
        self.assertEqual(17, len(parsed))

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

        self.assertEqual(24, len(parsed))


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
        





