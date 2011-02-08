#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_streets.searchInIndex import searchInIndex
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSearchLtStreetIndex_SingleStreet(TestCase):
    fixtures = ['ltstreetindexes/several ordinary streets.json']

    def setUp(self):
        pass

    def testSearchWithCity(self):
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        addresses = searchInIndex(municipality=municipality, city=city)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)
        self.assertEquals(2, len(addresses))

    def testSearchWithStreet(self):
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        street= u"Gedimino prospektas"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(1, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearch_CityMustBeLike(self):
        """ query for city must be like, not exactly equals, since this will ignore case"""
        # note that city is lowercase
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"vilnius"
        street= u"Gedimino prospektas"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(1, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearchWithStreet_Without_municipality(self):
        """ do not fail if municipality is empty and street is empty"""
        municipality = u""
        city=u"Kaunas"
        street= u""
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(3, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearchWithStreet_Without_municipality_2(self):
        """ do not fail if municipality is empty and street is not empty"""
        # street is exactly equal
        municipality = u""
        city=u"Kaunas"
        street= u"palemono gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(3, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearchWithStreet_Street_not_exactly_equal(self):
        """ street is not exactly equal. Do a like query"""
        municipality = u""
        city=u"Kaunas"
        street= u"palemon"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(3, addresses[0].id)
        self.assertEquals(1, len(addresses))


class TestSearchLtStreetIndex_StreetsWithNumbersInName(TestCase):
    fixtures = ['ltstreetindexes/streets with numbers in name.default.json']

    def setUp(self):
        pass

    def testSearch_RemoveStreetEnding(self):
        """ Street name is correct, but in the middle there should be numbers. So strip the last part from street
        The test fails, since the street is actually
        Antavilių sodų 1-oji gatvė
        Antavilių sodų 2-oji gatvė"""
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        street= u"Antavilių sodų gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)
        self.assertEquals(2, len(addresses))

    def testSearch_MoreThanOneResult_DoNotFailIfMuniciaplityIsEmpty(self):
        """ Remove street ending, municipality is empty"""
        municipality = u""
        city=u"Vilnius"
        street= u"Antavilių sodų gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)
        self.assertEquals(2, len(addresses))

    def testSearch_StreetIsNotExact_Needs_istartsWith(self):
        """ Street name is not exact, and exactly startswith query"""
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        street= u"Sodų gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([3], ids)
        self.assertEquals(1, len(addresses))
