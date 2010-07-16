#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianConstituencyReader
from contactdb.LTRegisterCenter.webparser import RegisterCenterParser, RegisterCenterPage, LinkCell
from settings import *

from urllib2 import urlopen

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

LietuvosRespublikaHtml = scriptPath + "/test data/LietuvosRespublika.htm", "http://www.registrucentras.lt/adr/p/index.php"
AlytausSavAlytausSenHtml = scriptPath + "/test data/AlytausSavAlytausSen.htm", "http://www.registrucentras.lt/adr/p/index.php?sen_id=5"
PagegiuSavNaktiskiuVillageHtml = scriptPath + "/test data/PagegiuSavNaktiskiuVillage.htm",


def ReadSource(sourceTag):
    """ Reads html file or URL address, or both, and returns it for testing routines """
    if (GlobalSettings.EnableWWWForLTGeoTests == True):
        if (len(sourceTag) > 1):
            response = urlopen(sourceTag[1])
            lines = "".join(response.readlines())
            yield lines

    file = open(sourceTag[0])
    lines = "".join(file.readlines())
    yield lines



class TestLTRegisterCenterOtherLinks(TestCase):

    def setUp(self):
        pass
        
    def assertPage(self, pageLinks, cells):
        """ Check that give collection of links is equal to cells collection
        pageLinks is a collection of LinkCell objects taken from RegisterCenterPage object
        cells is a list of LinkCell objects.
        """
        joined = zip(pageLinks, cells)

        for p, c in joined:
            if (c.href == ""):
                c.href = None
            self.assertEqual(p.text, c.text)
            self.assertEqual(p.href, c.href)

        self.assertEqual(len(cells), len(pageLinks))

    def testPagegiuSavNaktiskiuVillageHtml(self):
        for lines in ReadSource(PagegiuSavNaktiskiuVillageHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(len(page.otherPages), 0)

    def testLietuvosRespublika(self):
        for lines in ReadSource(LietuvosRespublikaHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(len(page.otherPages), 0)


    def testAlytausSavAlytausSenHtml(self):
        links = [
("2", "http://www.registrucentras.lt/adr/p/index.php?sen_id=5&p=2"),
("3", "http://www.registrucentras.lt/adr/p/index.php?sen_id=5&p=3")]
        
        cells = [LinkCell(tuple[0], tuple[1]) for tuple in links]

        for lines in ReadSource(AlytausSavAlytausSenHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.otherPages, cells)


class TestLTRegisterCenterLinks(TestCase):

    def setUp(self):
        pass

    def assertPage(self, pageLinks, cells):
        """ Check that give collection of links is equal to cells collection
        pageLinks is a collection of LinkCell objects taken from RegisterCenterPage object
        cells is a list of LinkCell objects.
        """

        joined = zip(pageLinks, cells)

        for p, c in joined:
            if (c.href == ""):
                c.href = None
            self.assertEqual(p.text, c.text)
            self.assertEqual(p.href, c.href)

        self.assertEqual(len(cells), len(pageLinks))

    def testPagegiuSavNaktiskiuVillageHtml(self):
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

        for lines in ReadSource(PagegiuSavNaktiskiuVillageHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.links, cells)

    def testAlytausSavAlytausSenHtml(self):
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


        for lines in ReadSource(AlytausSavAlytausSenHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.links, cells)




    def testLietuvosRespublika(self):
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

        for lines in ReadSource(LietuvosRespublikaHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.links, cells)




class TestLTRegisterCenterLocations(TestCase):

    def setUp(self):
        pass

    def testPagegiuSavNaktiskiuVillageHtml(self):
        for lines in ReadSource(PagegiuSavNaktiskiuVillageHtml):
            page = RegisterCenterParser(lines).parse()

            self.assertEqual(5, len(page.location))
            self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
            self.assertEqual("Tauragės apskr.", page.location[1])
            self.assertEqual("Pagėgių sav.", page.location[2])
            self.assertEqual("Natkiškių sen.", page.location[3])
            self.assertEqual("Natkiškių k.", page.location[4])

    def testAlytausSavAlytausSenHtml(self):
        for lines in ReadSource(AlytausSavAlytausSenHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(4, len(page.location))
            self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
            self.assertEqual("Alytaus apskr.", page.location[1])
            self.assertEqual("Alytaus r. sav.", page.location[2])
            self.assertEqual("Alytaus sen.", page.location[3])

    def testLietuvosRespublika(self):
        for lines in ReadSource(LietuvosRespublikaHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(1, len(page.location))
            self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0])
