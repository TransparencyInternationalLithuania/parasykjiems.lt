#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_civilparish.models import CivilParishStreet
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
        pass

class TestSearchInIndex(TestCase):

    def setUp(self):
        pass

    def testSearchGediminoStreet(self):
        pass