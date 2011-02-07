#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_civilparish.models import CivilParishStreet
from cdb_lt_mps.models import PollingDistrictStreet
from cdb_lt_streets.searchMembers import findCivilParishMembers, findLT_street_index_id
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )


class TestSearchCivilParishStreets_SingleStreet(TestCase):
    fixtures = ['kaimas.json']

    def setUp(self):
        pass

    def testSearch(self):
        municipality = u"Alytaus rajono savivaldybė"
        city=u"Aniškio kaimas"
        street=None
        house_number=None
        ids = findLT_street_index_id(modelToSearchIn=CivilParishStreet, municipality=municipality, city=city,  street=street, house_number=house_number)
        self.assertEquals([8], ids)

class TestSearchInstitutionStreets_WithStreetAndHouseNumber(TestCase):
    fixtures = ['several Gedimino 9, Vilnius MPs.json']

    municipality = u"Vilniaus miesto savivaldybė"
    city=u"Vilniaus miestas"
    street= u"Gedimino prospektas"

    def setUp(self):
        pass

    def testSearchOdd(self):
        """ we have two rows, but we need to find only the match with even house number""" 
        house_number=9
        ids = findLT_street_index_id(modelToSearchIn=PollingDistrictStreet, municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1], ids)

    def testSearch_Out_of_street_range(self):
        """ In case there are defined ranges for house numbers, but the provided house range is out of range, just return results for whole street"""
        house_number=14
        ids = findLT_street_index_id(modelToSearchIn=PollingDistrictStreet, municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1, 2], ids)

    def testSearch_DoNotIgnoreStreetpart(self):
        """ In case there are defined ranges for house numbers, but the provided house range is out of range, just return results for whole street.
        If our code would ignore street part, the result would be [2,4] not [2]"""

        house_number=10
        ids = findLT_street_index_id(modelToSearchIn=PollingDistrictStreet, municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([2], ids)

    def testSearchWhereStreetNumberHasNoRange(self):
        """ Sometimes individual houses will be listed, in that case query must be a bit different """
        house_number = 10
        ids = findLT_street_index_id(modelToSearchIn=PollingDistrictStreet, municipality=self.municipality, city=self.city,  street=u"Single ended house number street", house_number=house_number)
        self.assertEquals([3], ids)


class TestSearchInstitutionStreets_SingleRepresentative(TestCase):
    fixtures = ['single representative in street.json']

    municipality = u"Vilniaus miesto savivaldybė"
    city=u"Vilniaus miestas"
    street= u"Gedimino prospektas"

    def setUp(self):
        pass

    def testSearchSingleStreet(self):
        """ There are two streets by different name, find the correct one"""
        ids = findLT_street_index_id(modelToSearchIn=PollingDistrictStreet, municipality=self.municipality, city=self.city,  street=self.street)
        self.assertEquals([1], ids)

class TestSearchInIndex(TestCase):

    def setUp(self):
        pass

    def testSearchGediminoStreet(self):
        pass