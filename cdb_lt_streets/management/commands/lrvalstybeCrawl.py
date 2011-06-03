#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from cdb_lt_streets.crawlers.LRValstybe_lt.lrvalstybe_crawler import MunicipalityListReader, MunicipalityPageReader, MunicipalityContactReader, CivilParishListReader
from pjutils.timemeasurement import TimeMeasurer
import logging
from pjutils.uniconsole import *

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl [2:5]  to start from second source and finish in fifth"""

    def printCivilParish(self, municipalityName, municipalityUrl):
        print u"%s - %s" % (municipalityName, municipalityUrl)


        reader = MunicipalityPageReader(municipalityUrl)
        civilParishText, civilParishUrl =  reader.getCivilParishListUrl()
        print u"%s seniūnijų sąrašas %s - %s" % (municipalityName, civilParishText, civilParishUrl)



        for parish, url in CivilParishListReader(municipalityUrl, civilParishUrl).getCivilParishList():
            print u"Seniūnija: %s - %s" % (parish, url)
            if url is None:
                continue
            print "\n"
            reader = MunicipalityContactReader(url)
            print u"Seniūnai šioje seniūnijoje"
            for c in reader.getContactList():
                print "%s: %s, %s;" % (c.name, c.title, c.email)
        print "\n"


    def printMayors(self, municipalityName, municipalityUrl):
        print u"%s - %s" % (municipalityName, municipalityUrl)

        reader = MunicipalityPageReader(municipalityUrl)
        mayorText, mayorUrl = reader.getMayorUrl()
        print u"Nuoroda į mero puslapį %s - %s" % (mayorText, mayorUrl)


        reader = MunicipalityContactReader(mayorUrl)
        print u"Darbuotojai"
        for c in reader.getContactList():
            print "%s: %s, %s;" % (c.name, c.title, c.email)

        print "\n"


    def handle(self, *args, **options):
        timeMeasurer = TimeMeasurer()

        crawler = MunicipalityListReader(u"http://www.lrvalstybe.lt/savivaldybes-4906/")

        for municipalityName, municipalityUrl in list(crawler.getMunicipalityList()):
            #self.printCivilParish( municipalityName, municipalityUrl)
            self.printMayors( municipalityName, municipalityUrl)



        print "finished. Took %s seconds" % timeMeasurer.ElapsedSeconds()
