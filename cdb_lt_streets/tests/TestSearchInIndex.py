#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_civilparish.models import CivilParishStreet
from cdb_lt_mps.models import PollingDistrictStreet
from cdb_lt_streets.searchMembers import findCivilParishMembers, findLT_street_index_id
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSearchInIndex(TestCase):

    def setUp(self):
        pass

    def testSearchGediminoStreet(self):
        pass