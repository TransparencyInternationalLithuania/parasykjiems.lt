#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_streets.ltPrefixes import extractStreetEndingForm
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestExtractStreetEndingForm(TestCase):

    def setUp(self):
        pass

    def testExtractStreetEndig(self):
        self.assertEquals(u"", extractStreetEndingForm(u""))
        self.assertEquals(u"", extractStreetEndingForm(None))
        self.assertEquals(u"pr.", extractStreetEndingForm("gedimino pr."))