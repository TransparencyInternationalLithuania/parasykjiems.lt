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
    klaipedos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=111","Klaipėdos apskritis")
    marijampoles = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=161","Marijampolės apskritis")
    panevezio = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=204","Panevėžio apskritis")
    siauliu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=258","Šiaulių apskritis")
    taurages = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=322","Tauragės apskritis")
    telsiu = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=358","Telšių apskritis")
    utenos = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=392","Utenos apskritis")
    vilniaus = ("http://www.registrucentras.lt/adr/p/index.php?aps_id=460","Vilniaus apskritis")

    AllDistricts = [alytaus,
                     kauno,
                     klaipedos,
                     marijampoles,
                     panevezio,
                     siauliu,
                     taurages,
                     telsiu,
                     vilniaus]



class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl 2:5  to start from second source and finish in fifth"""

    def handle(self, *args, **options):

        timeMeasurer = TimeMeasurer()

        fromNumber = 0
        toNumber = len(RegisterCenterPageLocations.AllDistricts)

        if (len(args) >= 1):
            parts = args[0].split(":")
            if (len(parts) >= 1):
                if (parts[0].strip() != u""):
                    fromNumber = int(parts[0])
            if (len(parts) >= 2):
                if (parts[1].strip() != u""):
                    toNumber = int(parts[1])

        print "Will crawl from %s to %s source " % (fromNumber, toNumber)

        list = RegisterCenterPageLocations.AllDistricts[fromNumber:toNumber]


        print "Following pages will be parsed:"
        for i in list:
            url, name = i
            print "%s \t %s" % (name, url)


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
