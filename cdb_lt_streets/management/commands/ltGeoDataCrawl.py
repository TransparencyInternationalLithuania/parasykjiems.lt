#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
import types
import time
from contactdb.management.commands.importAll import ExecManagementCommand
import os
import logging

logger = logging.getLogger(__name__)

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
    telsiu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=358", os.path.join(commonPath, "Telsiu apskritis%s" % fileType))
    utenos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=392", os.path.join(commonPath, "Utenos apskritis%s" % fileType))
    vilniaus = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=460", os.path.join(commonPath, "Vilniaus apskritis%s" % fileType))

    # third option is the nominative form of City. This will be passed also as param --city when calling ltGeoDataExportCsv
    vilniusStreets = ("http://www.registrucentras.lt/adr/p/index.php?gyv_id=1", os.path.join(commonPath, "city_Vilnius%s" % fileType), "Vilnius")
    kaunasStreets = ("http://www.registrucentras.lt/adr/p/index.php?gyv_id=6", os.path.join(commonPath, "city_Kaunas%s" % fileType), "Kaunas")

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

def ExtractRange(args):
    fromNumber = 0
    toNumber = None
    parts = args.strip("[]").split(":")
    if (len(parts) >= 1):
        if (parts[0].strip() != u""):
            fromNumber = int(parts[0])
    if (len(parts) >= 2):
        if (parts[1].strip() != u""):
            toNumber = int(parts[1])
    return fromNumber, toNumber


class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl [2:5]  to start from second source and finish in fifth"""

    def handle(self, *args, **options):

        timeMeasurer = TimeMeasurer()

        if (len(args) >= 1):
            fromNumber, toNumber = ExtractRange(args[0])
        if (toNumber is None):
            toNumber = len(RegisterCenterPageLocations.AllData)


        print "Will crawl from %s to %s source " % (fromNumber, toNumber)

        list = RegisterCenterPageLocations.AllData[fromNumber:toNumber]


        print "Following pages will be parsed:"
        num = 0
        for i in list:
            # a weird way to unpack values
            url = i[0]
            name = i[1]
            city = u""
            if (len(i) >= 3):
                city = i[2]
            print "%s-%s  %s %s" % (num, name, url, city)
            num += 1


        seconds = 5
        print "Is that ok? Will wait for %s seconds" % (seconds)
        time.sleep(seconds)



        commands = []

        for location in list:
            url = location[0]
            name = location[1]
            commands.append("ltGeoDataClearQueue")
            #commands.append("ltGeoDataClearData")
            #commands.append(("ltGeoDataImportRC", {"url" : url, "max-depth" : 99}))
            exportOptions = {"file" : name}
            if (len(location) >= 2):
                exportOptions["city"] = location[2]
            commands.append(("ltGeoDataExportCsv", exportOptions))



        print "Will issue these commands:"
        for i in commands:
            print i

        print "Starting crawling"

        ExecManagementCommand(commands)

        print "finished. Took %s seconds" % timeMeasurer.ElapsedSeconds()
