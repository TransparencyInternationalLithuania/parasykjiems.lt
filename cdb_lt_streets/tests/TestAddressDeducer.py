#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *
from cdb_lt_streets.searchInIndex import deduceAddress

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestAddressDeducer(TestCase):
    def setUp(self):
        pass

    def testStreet_WithouCommaSeparataion_from_City(self):
        address = deduceAddress(u"gaidžių g. vilnius")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"gaidžių g.", address.street)
        self.assertEqual(u"vilnius", address.city)
        self.assertEqual(u"", address.municipality)

    def testGedimino_NoCity(self):
        """ basic test"""
        address = deduceAddress(u"Gedimino pr. 9")
        self.assertEqual(u"9", address.number)
        self.assertEqual(u"Gedimino pr.", address.street)
        self.assertEqual(u"", address.city)
        self.assertEqual(u"", address.municipality)

    def testGedimino_NoCity_NoNumber(self):
        address = deduceAddress(u"Gedimino pr.")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Gedimino pr.", address.street)
        self.assertEqual(u"", address.city)
        self.assertEqual(u"", address.municipality)


    def testGedimino(self):
        """ basic test"""
        address = deduceAddress(u"Gedimino pr. 9, Vilnius")
        self.assertEqual(u"9", address.number)
        self.assertEqual(u"Gedimino pr.", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"", address.municipality)

    def testSausio13_with_flat_number_and_number_in_street_name(self):
        address = deduceAddress(u"Sausio 13-osios g., Vilnius")
        self.assertEqual(u"", address.flatNumber)
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Sausio 13-osios g.", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"", address.municipality)

    def testSilenu_with_flat_number_and_letter(self):
        address = deduceAddress(u"Šilėnų g. 5A, Šiauliai")
        self.assertEqual(u"", address.flatNumber)
        self.assertEqual(u"5A", address.number)
        self.assertEqual(u"Šilėnų g.", address.street)
        self.assertEqual(u"Šiauliai", address.city)
        self.assertEqual(u"", address.municipality)

    def testSausio_street_with_number_in_name_with_street_part_no_comma(self):
        address = deduceAddress(u"Sausio 13-osios gatvė Vilnius")
        self.assertEqual(u"", address.flatNumber)
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Sausio 13-osios gatvė", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"", address.municipality)

    def testSausio_street_with_number_in_name(self):
        address = deduceAddress(u"Sausio 13-osios, Vilnius")
        self.assertEqual(u"", address.flatNumber)
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Sausio 13-osios", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"", address.municipality)

    def testSausio_street_with_number_in_name_no_city(self):
        address = deduceAddress(u"Sausio 13-osios")
        self.assertEqual(u"", address.flatNumber)
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Sausio 13-osios", address.street)
        self.assertEqual(u"", address.city)
        self.assertEqual(u"", address.municipality)

    def testSausio_street_with_number_in_name_no_city_with_street_part(self):
        address = deduceAddress(u"Sausio 13-osios gatvė")
        self.assertEqual(u"", address.flatNumber)
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Sausio 13-osios gatvė", address.street)
        self.assertEqual(u"", address.city)
        self.assertEqual(u"", address.municipality)


    def testGedimino_with_flat_number(self):
        address = deduceAddress(u"Gedimino 9-15, Vilnius")
        self.assertEqual(u"15", address.flatNumber)
        self.assertEqual(u"9", address.number)
        self.assertEqual(u"Gedimino", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"", address.municipality)

    def testWithCitySuffix(self):
        """  """
        address = deduceAddress(u"Pugainių kaimas")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"", address.street)
        self.assertEqual(u"Pugainių kaimas", address.city)
        self.assertEqual(u"", address.municipality)

    def testVerkiu(self):
        """ adds municipality """
        address = deduceAddress(u"Verkių g., Vilnius, Vilniaus m. sav.")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Verkių g.", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"Vilniaus m. sav.", address.municipality)

    def testDubenai(self):
        """ has no street part"""
        address = deduceAddress(u"Dubėnai, Alytaus r. sav.")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"", address.street)
        self.assertEqual(u"Dubėnai", address.city)
        self.assertEqual(u"Alytaus r. sav.", address.municipality)

    def testDubenaiNoMunicipality_with_short_generic_part(self):
        address = deduceAddress(u"Dubėnų k.")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"", address.street)
        self.assertEqual(u"Dubėnų k.", address.city)
        self.assertEqual(u"", address.municipality)

    def testDubenaiNoMunicipality(self):
        """ has no street part"""
        address = deduceAddress(u"Dubėnai")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"", address.street)
        self.assertEqual(u"Dubėnai", address.city)
        self.assertEqual(u"", address.municipality)

    def testVerkiai_NoCommas(self):
        """ no commas in addresses """
        address = deduceAddress(u"Verkių g. 30 Vilnius Vilniaus m. sav.")
        self.assertEqual(u"30", address.number)
        self.assertEqual(u"Verkių g.", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"Vilniaus m. sav.", address.municipality)


        # test with lots of spaces 
        address = deduceAddress(u"Verkių g. 30 Vilnius Vilniaus     m.     sav.")
        self.assertEqual(u"30", address.number)
        self.assertEqual(u"Verkių g.", address.street)
        self.assertEqual(u"Vilnius", address.city)
        self.assertEqual(u"Vilniaus m. sav.", address.municipality)

    def testStreetMunicipalityAndCity(self):
        """  """
        address = deduceAddress(u"mickevičiaus g., obelių miestas rokiškis")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"mickevičiaus g.", address.street)
        self.assertEqual(u"obelių miestas", address.city)
        self.assertEqual(u"rokiškis", address.municipality)

    def testStreetMunicipalityAndCity_2_no_comma(self):
        """  """
        address = deduceAddress(u"mickevičiaus g. obelių miestas rokiškis")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"mickevičiaus g.", address.street)
        self.assertEqual(u"obelių miestas", address.city)
        self.assertEqual(u"rokiškis", address.municipality)

    def testLongCityAndMunicipalityNames(self):
        """ This fails: Žalioji gatvė,  Senųjų Trakų kaimas, Trakų rajono savivaldybė"""

        address = deduceAddress(u"Žalioji gatvė,  Senųjų Trakų kaimas, Trakų rajono savivaldybė")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"Žalioji gatvė", address.street)
        self.assertEqual(u"Senųjų Trakų kaimas", address.city)
        self.assertEqual(u"Trakų rajono savivaldybė", address.municipality)

    def testWithCivilParish(self):
        address = deduceAddress(u"Miroslavo kaimas, Miroslavo seniūnija, Alytaus rajono savivaldybė")
        self.assertEqual(u"", address.number)
        self.assertEqual(u"", address.street)
        self.assertEqual(u"Miroslavo kaimas", address.city)
        self.assertEqual(u"Miroslavo seniūnija", address.civilParish)
        self.assertEqual(u"Alytaus rajono savivaldybė", address.municipality)


    def testWithCivilParish_and_street(self):
        address = deduceAddress(u"Šiltnamių gatvė 18, Pagirių kaimas, Pagirių seniūnija, Vilniaus rajono savivaldybė")
        self.assertEqual(u"18", address.number)
        self.assertEqual(u"Šiltnamių gatvė", address.street)
        self.assertEqual(u"Pagirių kaimas", address.city)
        self.assertEqual(u"Pagirių seniūnija", address.civilParish)
        self.assertEqual(u"Vilniaus rajono savivaldybė", address.municipality)






