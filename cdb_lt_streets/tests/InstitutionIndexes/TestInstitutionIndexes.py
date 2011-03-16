#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_streets.searchMembers import findLT_street_index_id
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSearchCivilParishStreets_SingleStreet(TestCase):
    fixtures = ['InstitutionIndexes/kaimas.json']

    def setUp(self):
        pass

    def testSearch(self):
        municipality = u"Alytaus rajono savivaldybė"
        city=u"Aniškio kaimas"
        street=None
        house_number=None
        ids = findLT_street_index_id(municipality=municipality, city=city,  street=street, house_number=house_number)
        self.assertEquals([8], ids)

class TestSearchInstitutionStreets_WithStreetAndHouseNumber(TestCase):
    fixtures = ['InstitutionIndexes/several Gedimino 9, Vilnius MPs.json']

    municipality = u"Vilniaus miesto savivaldybė"
    city=u"Vilniaus miestas"
    street= u"Gedimino prospektas"

    def setUp(self):
        pass

    def testSearchOdd(self):
        """ we have two rows, but we need to find only the match with even house number"""
        house_number=9
        ids = findLT_street_index_id(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1], ids)

    def testSearch_Out_of_street_range(self):
        """ In case there are defined ranges for house numbers, but the provided house range is out of range, just return results for whole street"""
        house_number=14
        ids = findLT_street_index_id(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1, 2], ids)

    def testSearch_DoNotIgnoreStreetpart(self):
        """ In case there are defined ranges for house numbers, but the provided house range is out of range, just return results for whole street.
        If our code would ignore street part, the result would be [2,4] not [2]"""

        house_number=10
        ids = findLT_street_index_id(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([2], ids)

    def testSearchWhereStreetNumberHasNoRange(self):
        """ Sometimes individual houses will be listed, in that case query must be a bit different """
        house_number = 10
        ids = findLT_street_index_id(municipality=self.municipality, city=self.city,  street=u"Single ended house number street", house_number=house_number)
        self.assertEquals([3], ids)

    def testSearch_Multiple_Results_ForDStreet(self):
        """ Single streets has more than one representative, but house number is not given  """
        house_number = None
        ids = findLT_street_index_id(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1,2], ids)


class TestSearchInstitutionStreets_SingleRepresentative(TestCase):
    fixtures = ['InstitutionIndexes/single representative in street.json']

    municipality = u"Vilniaus miesto savivaldybė"
    city=u"Vilniaus miestas"
    street= u"Gedimino prospektas"

    def setUp(self):
        pass

    def testSearchSingleStreet(self):
        """ There are two streets by different name, find the correct one"""
        ids = findLT_street_index_id(municipality=self.municipality, city=self.city,  street=self.street)
        self.assertEquals([1], ids)

class TestSearchInstitutionStreets_ArminuKaimas(TestCase):
    fixtures = ['InstitutionIndexes/arminu i kaimas.json']

    def setUp(self):
        pass

    def testSearchWhenStreetIsNOne(self):
        """ When street is "" or None, results must be same"""
        ids = findLT_street_index_id(municipality=u"Alytaus rajono savivaldybė", city=u"Arminų I kaimas",  street=None)
        self.assertEquals([8, 12], ids)

    def testSearchWhenStreetIsNOne(self):
        ids = findLT_street_index_id(municipality=u"Alytaus rajono savivaldybė", civilParish=u"Krokialaukio seniūnija", city=u"Arminų I kaimas",  street=None)
        self.assertEquals([12], ids)

class TestSearchInstitutionStreets_NumberToIsNone(TestCase):
    fixtures = ['InstitutionIndexes/number To is None.json']

    def setUp(self):
        pass

    def testSearchNumberToIsNone(self):
        """ Data contains exact house value: numberFrom is give, numberTo is None.
        Query should consider that numberTo might be None, but not necesarrily"""
        ids = findLT_street_index_id(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number=9)
        self.assertEquals([1], ids)

class TestSearchInstitutionStreets_NumberWithLetter(TestCase):
    fixtures = ['InstitutionIndexes/number with letter.json']

    def setUp(self):
        pass

    def testSearchNumberWithLetter(self):
        """ Data contains exact house value: numberFrom is give, numberTo is None.
        Query should consider that numberTo might be None, but not necesarrily"""
        ids = findLT_street_index_id(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number=9)
        self.assertEquals([2], ids)

        ids = findLT_street_index_id(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number="9A")
        self.assertEquals([1], ids)

    def testSearchNumberWithLetter_Letter_is_in_another_house_range(self):
        """ One street from 10 to 20, another street 14a    Should find correctly one or another"""
        ids = findLT_street_index_id(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Vaižganto gatvė", house_number="56")
        self.assertEquals([3], ids)

        ids = findLT_street_index_id(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Vaižganto gatvė", house_number="56A")
        self.assertEquals([4], ids)

    def testSearchNumberWithLetter_Letter_is_lowercaes(self):
        """ All house numbers if contains letter, data must be in uppercase. However, if we query with lowercase, still find it """
        ids = findLT_street_index_id(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Vaižganto gatvė", house_number="56a")
        self.assertEquals([4], ids)