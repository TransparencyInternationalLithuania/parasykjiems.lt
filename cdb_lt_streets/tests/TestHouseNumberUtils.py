#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_streets.houseNumberUtils import ContainsHouseNumbers
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )



class TestContainsHouseNumbers(TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        self.assertEqual(True, ContainsHouseNumbers("Gedimino 9a"))

    def testBasic2(self):
        self.assertEqual(False, ContainsHouseNumbers("Gedimino 9-"))

    def testBasic2(self):
        self.assertEqual(False, ContainsHouseNumbers("Sausio 13-osios g."))
        self.assertEqual(True, ContainsHouseNumbers("Sausio 13-osios g. 5"))

