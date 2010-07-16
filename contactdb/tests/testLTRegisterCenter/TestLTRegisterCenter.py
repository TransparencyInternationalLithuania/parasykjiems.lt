#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianConstituencyReader
from contactdb.LTRegisterCenter.webparser import RegisterCenterParser, RegisterCenterPage, LinkCell

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

LietuvosRespublikaHtml = scriptPath + "/test data/LietuvosRespublika.htm"
AlytausSavAlytausSenHtml = scriptPath + "/test data/AlytausSavAlytausSen.htm"
PagegiuSavNaktiskiuVillageHtml = scriptPath + "/test data/PagegiuSavNaktiskiuVillage.htm"



class TestLTRegisterCenterLinks(TestCase):

    def setUp(self):
        pass

    def assertPage(self, page, cells):

        joined = zip(page.links, cells)

        for p, c in joined:
            if (c.href == ""):
                c.href = None 
            self.assertEqual(p.text, c.text)
            self.assertEqual(p.href, c.href)

        self.assertEqual(len(cells), len(page.links))

    def testPagegiuSavNaktiskiuVillageHtml(self):
        file = open(PagegiuSavNaktiskiuVillageHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()

        streets = ["Alyvų g.",
"Ąžuolo g.",
"Zosės Petraitienės g.",
"Pievų g.",
"Putinų g.",
"Saulėtekio g.",
"Sodo g.",
"Vilties g.",
"Vingio g."]
        cells = [LinkCell(street, "") for street in streets]
        self.assertPage(page, cells)

    def testAlytausSavAlytausSenHtml(self):
        file = open(AlytausSavAlytausSenHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()

        villages = [
("Aniškio k.", ""),
("Arminų I k.", ""),
("Arminų II k.", ""),
("Bakšių k.", ""),
("Bernotiškių k.", ""),
("Bundorių k.", ""),
("Butkūnų k.", ""),
("Butrimiškių k.", ""),
("Daugirdėlių k.", ""),
("Daujotiškių k.", ""),
("Dubenkos k.", ""),
("Dubėnų k.", ""),
("Dubių k.", ""),
("Genių k.", "") ,
("Jasunskų k.", ""),
("Jovaišonių k.", ""),
("Junonių k.", ""),
("Jurgiškių k.", ""),
("Kaniūkų k.", ""),
("Karklynų k.", ""),
("Kelmanonių k.", ""),
("Kibirkščių k.", ""),
("Kriaunių k.", ""),
("Likiškėlių k.", "http://www.registrucentras.lt/adr/p/index.php?gyv_id=339"),
("Likiškių k.", "")]
        cells = [LinkCell(tuple[0], tuple[1]) for tuple in villages]
        self.assertPage(page, cells)

        

    def testLietuvosRespublika(self):
        file = open(LietuvosRespublikaHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()
        cells = [
            LinkCell(text="Alytaus apskr.",     href="http://www.registrucentras.lt/adr/p/index.php?aps_id=1"),
            LinkCell(text="Kauno apskr.",       href="http://www.registrucentras.lt/adr/p/index.php?aps_id=41"),
            LinkCell(text="Klaipėdos apskr.",   href="http://www.registrucentras.lt/adr/p/index.php?aps_id=111"),
            LinkCell(text="Marijampolės apskr.",href="http://www.registrucentras.lt/adr/p/index.php?aps_id=161"),
            LinkCell(text="Panevėžio apskr.",   href="http://www.registrucentras.lt/adr/p/index.php?aps_id=204"),
            LinkCell(text="Šiaulių apskr.",     href="http://www.registrucentras.lt/adr/p/index.php?aps_id=258"),
            LinkCell(text="Tauragės apskr.",    href="http://www.registrucentras.lt/adr/p/index.php?aps_id=322"),
            LinkCell(text="Telšių apskr.",      href="http://www.registrucentras.lt/adr/p/index.php?aps_id=358"),
            LinkCell(text="Utenos apskr.",      href="http://www.registrucentras.lt/adr/p/index.php?aps_id=392"),
            LinkCell(text="Vilniaus apskr.",    href="http://www.registrucentras.lt/adr/p/index.php?aps_id=460"),
        ]
        self.assertPage(page, cells)





class TestLTRegisterCenterLocations(TestCase):

    def setUp(self):
        pass

    def testPagegiuSavNaktiskiuVillageHtml(self):
        file = open(PagegiuSavNaktiskiuVillageHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()

        self.assertEqual(5, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
        self.assertEqual("Tauragės apskr.", page.location[1])
        self.assertEqual("Pagėgių sav.", page.location[2])
        self.assertEqual("Natkiškių sen.", page.location[3])
        self.assertEqual("Natkiškių k.", page.location[4])

    def testAlytausSavAlytausSenHtml(self):
        file = open(AlytausSavAlytausSenHtml)
        lines = "\n".join(file.readlines())
        page = RegisterCenterParser(lines).parse()
        self.assertEqual(4, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
        self.assertEqual("Alytaus apskr.", page.location[1])
        self.assertEqual("Alytaus r. sav.", page.location[2])
        self.assertEqual("Alytaus sen.", page.location[3])

    def testLietuvosRespublika(self):
        file = open(LietuvosRespublikaHtml)
        lines = "".join(file.readlines())
        page = RegisterCenterParser(lines).parse()
        self.assertEqual(1, len(page.location))
        self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
