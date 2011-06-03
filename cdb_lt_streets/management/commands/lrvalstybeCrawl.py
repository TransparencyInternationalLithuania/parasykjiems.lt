#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from cdb_lt_streets.crawlers.LRValstybe_lt.lrvalstybe_crawler import MunicipalityListReader, MunicipalityPageReader, MunicipalityContactReader
from pjutils.timemeasurement import TimeMeasurer
import logging
from pjutils.uniconsole import *

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl [2:5]  to start from second source and finish in fifth"""

    def handle(self, *args, **options):
        timeMeasurer = TimeMeasurer()

        crawler = MunicipalityListReader(u"http://www.lrvalstybe.lt/savivaldybes-4906/")

        for text, url in list(crawler.getMunicipalityList())[46:47]:
            print "%s - %s" % (text, url)

            municipalityUrl = u"%s%s" % ("http://www.lrvalstybe.lt", url)
            reader = MunicipalityPageReader(municipalityUrl)
            mayorText, mayorUrl = reader.getMayorUrl()
            print "Mayor %s - %s" % (mayorText, mayorUrl)


            mayorUrl = u"%s%s" % ("http://www.lrvalstybe.lt", mayorUrl)
            reader = MunicipalityContactReader(mayorUrl)
            for c in reader.getContactList():
                print "Contact: %s %s %s" % (c.name, c.title, c.email)
            print "\n"

        print "finished. Took %s seconds" % timeMeasurer.ElapsedSeconds()
