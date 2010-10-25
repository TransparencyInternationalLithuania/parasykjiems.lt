#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
import types
import time
from contactdb.management.commands.importAll import ExecManagementCommand

class RegisterCenterPageLocations:
    alytaus = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=1", "Alytaus apskritis")
    kauno = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=41","Kauno apskritis")
    klaipedos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=111","Klaipedos apskritis")
    marijampoles = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=161","Marijampoles apskritis")
    panevezio = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=204","Panevezio apskritis")
    siauliu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=258","Siauliu apskritis")
    taurages = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=322","Taurages apskritis")
    telsiu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=358","Telsių apskritis")
    utenos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=392","Utenos apskritis")
    vilniaus = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=460","Vilniaus apskritis")

    vilniusStreets = ("http://www.registrucentras.lt/adr/p/index.php?gyv_id=1", "city_Vilnius")
    kaunasStreets = ("http://www.registrucentras.lt/adr/p/index.php?gyv_id=6", "city_Kaunas")

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
            name = name.replace(" ", "")
            commands.append("ltGeoDataClearData")
            commands.append("ltGeoDataClearQueue")
            commands.append(("ltGeoDataImportRC", {"url" : url, "max-depth" : 99}))
            commands.append(("ltGeoDataExportCsv", {"file" : "%s.csv" % (name)}))



        print "Will issue these commands:"
        for i in commands:
            print i

        print "Starting crawling"

        ExecManagementCommand(commands)

        print "finished. Took %s seconds" % timeMeasurer.ElapsedSeconds()
