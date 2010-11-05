#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
import types
import time
from contactdb.management.commands.importAll import ExecManagementCommand
import os

class RegisterCenterPageLocations:
    fileType = ".csv"
    commonPath = os.path.join("contactdb", "sources", "register center", "municipalities")

    alytaus = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=1", os.path.join(commonPath, "Alytaus apskritis%s" % fileType))
    kauno = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=41", os.path.join(commonPath, "Kauno apskritis%s" % fileType))
    klaipedos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=111", os.path.join(commonPath, "Klaipedos apskritis%s" % fileType))
    marijampoles = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=161", os.path.join(commonPath, "Marijampoles apskritis%s" % fileType))
    panevezio = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=204", os.path.join(commonPath, "Panevezio apskritis%s" % fileType))
    siauliu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=258", os.path.join(commonPath, "Siauliu apskritis%s" % fileType))
    taurages = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=322", os.path.join(commonPath, "Taurages apskritis%s" % fileType))
    telsiu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=358", os.path.join(commonPath, "Telsių apskritis%s" % fileType))
    utenos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=392", os.path.join(commonPath, "Utenos apskritis%s" % fileType))
    vilniaus = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=460", os.path.join(commonPath, "Vilniaus apskritis%s" % fileType))

    vilniusStreets = ("http://www.registrucentras.lt/adr/p/index.php?gyv_id=1", os.path.join(commonPath, "city_Vilnius%s" % fileType))
    kaunasStreets = ("http://www.registrucentras.lt/adr/p/index.php?gyv_id=6", os.path.join(commonPath, "city_Kaunas%s" % fileType))

    allStreets = [vilniusStreets,
                kaunasStreets]

    AllDistricts = [alytaus,
                     kauno,
                     klaipedos,
                     marijampoles,
                     panevezio,
                     siauliu,
                     taurages,
                     telsiu,
                     utenos,
                     vilniaus]

    AllData = AllDistricts + allStreets


class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl [2:5]  to start from second source and finish in fifth"""

    def handle(self, *args, **options):

        timeMeasurer = TimeMeasurer()

        fromNumber = 0
        toNumber = len(RegisterCenterPageLocations.AllData)

        if (len(args) >= 1):
            parts = args[0].strip("[]").split(":")
            if (len(parts) >= 1):
                if (parts[0].strip() != u""):
                    fromNumber = int(parts[0])
            if (len(parts) >= 2):
                if (parts[1].strip() != u""):
                    toNumber = int(parts[1])

        print "Will crawl from %s to %s source " % (fromNumber, toNumber)

        list = RegisterCenterPageLocations.AllData[fromNumber:toNumber]


        print "Following pages will be parsed:"
        num = 0
        for i in list:
            url, name = i
            print "%s-%s  %s" % (num, name, url)
            num += 1


        seconds = 5
        print "Is that ok? Will wait for %s seconds" % (seconds)
        time.sleep(seconds)



        commands = []

        for location in list:
            url, name = location
            commands.append("ltGeoDataClearQueue")
            #commands.append("ltGeoDataClearData")
            #commands.append(("ltGeoDataImportRC", {"url" : url, "max-depth" : 99}))
            commands.append(("ltGeoDataExportCsv", {"file" : name}))



        print "Will issue these commands:"
        for i in commands:
            print i

        print "Starting crawling"

        ExecManagementCommand(commands)

        print "finished. Took %s seconds" % timeMeasurer.ElapsedSeconds()
