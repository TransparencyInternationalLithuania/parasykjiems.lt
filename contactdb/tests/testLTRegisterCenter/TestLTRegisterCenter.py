#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianConstituencyReader
from contactdb.LTRegisterCenter.webparser import RegisterCenterParser, RegisterCenterPage

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestLTRegisterCenter(TestCase):

    LietuvosRespublikaHtml = scriptPath + "/test data/LietuvosRespublika.htm"

    def setUp(self):
        pass

    def testLietuvosRespublika(self):
        file = open(self.LietuvosRespublikaHtml)
        lines = "".join(file.readlines())
        page = RegisterCenterParser(lines).parse()
        self.assertEqual(1, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
