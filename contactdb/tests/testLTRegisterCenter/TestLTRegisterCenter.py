#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianConstituencyReader

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestLTRegisterCenter(TestCase):

    LietuvosRespublikaHtml = scriptPath + "/test data/LietuvosRespublika.htm"

    def setUp(self):
        pass

    def testLietuvosRespublika(self):
        pass
        