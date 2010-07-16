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
    AlytausSavAlytausSenHtml = scriptPath + "/test data/AlytausSavAlytausSen.htm"
    PagegiuSavNaktiskiuVillageHtml = scriptPath + "/test data/PagegiuSavNaktiskiuVillage.htm"

    def setUp(self):
        pass

    def testPagegiuSavNaktiskiuVillageHtml(self):
        file = open(self.PagegiuSavNaktiskiuVillageHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()

        self.assertEqual(5, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
        self.assertEqual("Tauragės apskr.", page.location[1])
        self.assertEqual("Pagėgių sav.", page.location[2])
        self.assertEqual("Natkiškių sen.", page.location[3])
        self.assertEqual("Natkiškių k.", page.location[4])

    def testAlytausSavAlytausSenHtml(self):
        file = open(self.AlytausSavAlytausSenHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()
        self.assertEqual(4, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
        self.assertEqual("Alytaus apskr.", page.location[1])
        self.assertEqual("Alytaus r. sav.", page.location[2])
        self.assertEqual("Alytaus sen.", page.location[3])

    def testLietuvosRespublika(self):
        file = open(self.LietuvosRespublikaHtml)
        lines = "".join(file.readlines())
        page = RegisterCenterParser(lines).parse()
        self.assertEqual(1, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
