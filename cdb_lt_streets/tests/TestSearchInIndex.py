#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSearchInIndex(TestCase):
    #fixtures = ['municipality.vilnius.json']

    def setUp(self):
        pass

    def testSearchGediminoStreet(self):
        pass