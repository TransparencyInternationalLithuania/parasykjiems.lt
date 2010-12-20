#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *
from cdb_lt_streets.searchInIndex import deduceAddress

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )



class TestAddressDeducer(TestCase):
    def setUp(self):
        pass

    def testGedimino_NoCity(self):
        """ basic test"""
        address = deduceAddress(u"Gedimino pr. 9")
        self.assertEqual(u"9", address.number)
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

    def testGedimino_with_flat_number(self):
        address = deduceAddress(u"Gedimino 9-15, Vilnius")
        self.assertEqual(u"15", address.flatNumber)
        self.assertEqual(u"9", address.number)
        self.assertEqual(u"Gedimino", address.street)
        self.assertEqual(u"Vilnius", address.city)
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



class TestSearchInIndex(TestCase):
    #fixtures = ['municipality.vilnius.json']

    def setUp(self):
        pass

    def testSearchGediminoStreet(self):
        pass