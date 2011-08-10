#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *
from territories.stringUtils import stringIsIn


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestStringUtils(TestCase):

    def setUp(self):
        pass

    def testSinmple(self):
        self.assertEquals(True, stringIsIn(u"Seniūnas", [u"seniūnas"]))
        self.assertEquals(True, stringIsIn(u"seniūnas", [u"seniūnas"]))
        self.assertEquals(False, stringIsIn(u"Seniūnės pavaduotojas", [u"seniūnas", u"seniūnė"]))