#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from contactdb.AdressParser import AddressParser
from contactdb.imp import LithuanianConstituencyReader
from contactdb.LTRegisterCenter.webparser import RegisterCenterParser, RegisterCenterPage, LinkCell, LTGeoDataHierarchy
from settings import *
from contactdb.models import HierarchicalGeoData

from urllib2 import urlopen
import contactdb.models

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

LietuvosRespublikaHtml = scriptPath + "/test data/LietuvosRespublika.htm", "http://www.registrucentras.lt/adr/p/index.php"
AlytausSavAlytausSenHtml = scriptPath + "/test data/AlytausSavAlytausSen.htm", "http://www.registrucentras.lt/adr/p/index.php?sen_id=5"
PagegiuSavNaktiskiuVillageHtml = scriptPath + "/test data/PagegiuSavNaktiskiuVillage.htm",
AlytausSavAlytausSenLastPageHtml = scriptPath + "/test data/AlytausSavAlytausSenLastPage.htm", "http://www.registrucentras.lt/adr/p/index.php?sen_id=5&p=3"
AlytausSavHtml = scriptPath + "/test data/AlytausSav.htm", "http://www.registrucentras.lt/adr/p/index.php?sav_id=4"


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



    def testAlytausSavAlytausSenLastPageHtml(self):
        for lines in ReadSource(AlytausSavAlytausSenLastPageHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(len(page.otherPages), 2)

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
        streets = ["Alyvų gatvė",
"Ąžuolo gatvė",
"Zosės Petraitienės gatvė",
"Pievų gatvė",
"Putinų gatvė",
"Saulėtekio gatvė",
"Sodo gatvė",
"Vilties gatvė",
"Vingio gatvė"]
        cells = [LinkCell(street, "") for street in streets]

        for lines in ReadSource(PagegiuSavNaktiskiuVillageHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.links, cells)

    def testAlytausSavHtml(self):
        for lines in ReadSource(AlytausSavHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(len(page.links), 11)


    def testAlytausSavAlytausSenHtml(self):
        villages = [
("Aniškio kaimas", ""),
("Arminų I kaimas", ""),
("Arminų II kaimas", ""),
("Bakšių kaimas", ""),
("Bernotiškių kaimas", ""),
("Bundorių kaimas", ""),
("Butkūnų kaimas", ""),
("Butrimiškių kaimas", ""),
("Daugirdėlių kaimas", ""),
("Daujotiškių kaimas", ""),
("Dubenkos kaimas", ""),
("Dubėnų kaimas", ""),
("Dubių kaimas", ""),
("Genių kaimas", "") ,
("Jasunskų kaimas", ""),
("Jovaišonių kaimas", ""),
("Junonių kaimas", ""),
("Jurgiškių kaimas", ""),
("Kaniūkų kaimas", ""),
("Karklynų kaimas", ""),
("Kelmanonių kaimas", ""),
("Kibirkščių kaimas", ""),
("Kriaunių kaimas", ""),
("Likiškėlių kaimas", "http://www.registrucentras.lt/adr/p/index.php?gyv_id=339"),
("Likiškių kaimas", "")]
        cells = [LinkCell(tuple[0], tuple[1]) for tuple in villages]


        for lines in ReadSource(AlytausSavAlytausSenHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.links, cells)




    def testLietuvosRespublika(self):
        cells = [
            LinkCell(text="Alytaus apskritis",     href="http://www.registrucentras.lt/adr/p/index.php?aps_id=1"),
            LinkCell(text="Kauno apskritis",       href="http://www.registrucentras.lt/adr/p/index.php?aps_id=41"),
            LinkCell(text="Klaipėdos apskritis",   href="http://www.registrucentras.lt/adr/p/index.php?aps_id=111"),
            LinkCell(text="Marijampolės apskritis",href="http://www.registrucentras.lt/adr/p/index.php?aps_id=161"),
            LinkCell(text="Panevėžio apskritis",   href="http://www.registrucentras.lt/adr/p/index.php?aps_id=204"),
            LinkCell(text="Šiaulių apskritis",     href="http://www.registrucentras.lt/adr/p/index.php?aps_id=258"),
            LinkCell(text="Tauragės apskritis",    href="http://www.registrucentras.lt/adr/p/index.php?aps_id=322"),
            LinkCell(text="Telšių apskritis",      href="http://www.registrucentras.lt/adr/p/index.php?aps_id=358"),
            LinkCell(text="Utenos apskritis",      href="http://www.registrucentras.lt/adr/p/index.php?aps_id=392"),
            LinkCell(text="Vilniaus apskritis",    href="http://www.registrucentras.lt/adr/p/index.php?aps_id=460"),
        ]

        for lines in ReadSource(LietuvosRespublikaHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertPage(page.links, cells)




class TestLTRegisterCenterLocations(TestCase):

    def setUp(self):
        pass

    def testPagegiuSavNaktiskiuVillageHtml_Types(self):
       for lines in ReadSource(PagegiuSavNaktiskiuVillageHtml):
           page = RegisterCenterParser(lines).parse()

           self.assertEqual(5, len(page.location))
           for i in range(0, len(page.location)):
               self.assertEqual(LTGeoDataHierarchy.Hierarchy[i], page.location[i].type)

    def testPagegiuSavNaktiskiuVillageHtml(self):
        for lines in ReadSource(PagegiuSavNaktiskiuVillageHtml):
            page = RegisterCenterParser(lines).parse()

            self.assertEqual(5, len(page.location))
            self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0].text)
            self.assertEqual("Tauragės apskritis", page.location[1].text)
            self.assertEqual("Pagėgių savivaldybė", page.location[2].text)
            self.assertEqual("Natkiškių seniūnija", page.location[3].text)
            self.assertEqual("Natkiškių kaimas", page.location[4].text)

    def testAlytausSavAlytausSenHtml(self):
        for lines in ReadSource(AlytausSavAlytausSenHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(4, len(page.location))
            self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0].text)
            self.assertEqual("Alytaus apskritis", page.location[1].text)
            self.assertEqual("Alytaus savivaldybė", page.location[2].text)
            self.assertEqual("Alytaus seniūnija", page.location[3].text)

    def testLietuvosRespublika(self):
        for lines in ReadSource(LietuvosRespublikaHtml):
            page = RegisterCenterParser(lines).parse()
            self.assertEqual(1, len(page.location))
            self.assertEqual("LIETUVOS RESPUBLIKA", page.location[0].text)
