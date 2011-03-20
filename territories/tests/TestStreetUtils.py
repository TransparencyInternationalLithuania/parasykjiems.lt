#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *
from territories.ltPrefixes import extractStreetEndingForm
from territories.streetUtils import changeDoubleWordStreetToDot

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestExtractStreetEndingForm(TestCase):

    def setUp(self):
        pass

    def testExtractStreetEndig(self):
        self.assertEquals(u"", extractStreetEndingForm(u""))
        self.assertEquals(u"", extractStreetEndingForm(None))
        self.assertEquals(u"pr.", extractStreetEndingForm("gedimino pr."))
        self.assertEquals(u"g.", extractStreetEndingForm(u"Centrinės aikštės g."))
        #self.assertEquals(u"gatvė", extractStreetEndingForm(u"Centrinės aikštės gatvė"))
        #self.assertEquals(u"g.", extractStreetEndingForm(u"Žeimių g. 2"))


class TestChangeDoubleWordStreetToDot(TestCase):

    def setUp(self):
        pass

    def testExtractStreetEndig(self):
        self.assertEquals(u"", changeDoubleWordStreetToDot(u""))
        self.assertEquals(u"Šimonio", changeDoubleWordStreetToDot(u"Igno Šimonio"))
        self.assertEquals(u"Šimonio gatvė", changeDoubleWordStreetToDot(u"Igno Šimonio gatvė"))
        self.assertEquals(u"Gedimino prospektas", changeDoubleWordStreetToDot(u"Gedimino prospektas"))