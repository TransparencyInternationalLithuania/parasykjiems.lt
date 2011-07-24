#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from cdb_lt.management.commands.importSources import ltGeoDataSources_Country
from cdb_lt_streets.crawlers.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.management.commands.ltGeoDataClearQueue import clearQueue
from cdb_lt_streets.management.commands.ltGeoDataExportCsv import RCCrawledDataExporter
from cdb_lt_streets.management.commands.ltGeoDataImportRC import ltGeoDataWebScraper
from cdb_lt_streets.management.commands.ltGeoDataClearData import clearGeoData


from pjutils.MessagingServer.MessagingServer import MQServer
from pjutils.args.Args import ExtractRange

from pjutils.timemeasurement import TimeMeasurer
import time
import os
import logging
from pjutils.djangocommands import ExecManagementCommand

logger = logging.getLogger(__name__)

class RegisterCenterPageLocations:
    fileType = ".csv"
    commonPath = os.path.join("contactdb", "sources", "import data", "municipalities")

    vilniusStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=1", {'city': u"Vilnius"})
    kaunasStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=6", {'city': u"Kaunas"})
    alytusStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=2", {'city': u"Alytus"})
    klaipedaStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=7", {'city': u"Klaipėda"})
    marijampolesStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=5",  {'city': u"Marijampolė"})
    panevezioStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=10",  {'city': u"Panevėžys"})
    siauliuStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=11", {'city': u"Šiauliai"})
    taurageStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=82", {'city': u"Tauragė", 'insertCivilParish': False})
    telsiuStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=84",  {'city': u"Telšiai", 'insertCivilParish': False})
    utenaStreets = (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=93", {'city': u"Utena", 'insertCivilParish': False})

    allStreets = [
            alytusStreets,
            kaunasStreets,
            klaipedaStreets,
            marijampolesStreets,
            panevezioStreets,
            siauliuStreets,
            taurageStreets,
            telsiuStreets,
            utenaStreets,
            vilniusStreets]

    additionalCities = [
        (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=8", {'city' : u"Neringa"}),
        (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=9", {'city' : u"Palanga"}),
        (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=33", {'city' : u"Visaginas"}),
        (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=4", {'city' : u"Druskininkai"}),
        (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=61", {'city' : u"Molėtai"}),
        (u"http://www.registrucentras.lt/adr/p/index.php?gyv_id=39", {'city' : u"Kazlų Rūda"})
    ]

    AllMunicipalities = [
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=1",), #, "Alytaus apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=41",), #"Kauno apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=111",), #"Klaipedos apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=161",), #"Marijampoles apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=204",), #"Panevezio apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=258",), #"Siauliu apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=322",), #"Taurages apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=358",), #"Telsiu apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=392",), #"Utenos apskritis%s"
            (u"http://www.registrucentras.lt/adr/p/index.php?aps_id=460",), #"Vilniaus apskritis%s"
    ]

    AllData = AllMunicipalities + allStreets + additionalCities


class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl [2:5]  to start from second source and finish in fifth"""

    def handle(self, *args, **options):
        timeMeasurer = TimeMeasurer()

        zipped = zip(RegisterCenterPageLocations.AllData, ltGeoDataSources_Country.LithuanianAddresses)

        fromNumber = 0
        toNumber = None
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])
        if toNumber is None:
            toNumber = len(zipped)

        print "Will crawl from %s to %s source " % (fromNumber, toNumber)

        list = zipped[fromNumber:toNumber]

        print "Following pages will be parsed:"
        num = 0
        for location in list:
            # a weird way to unpack values
            url = location[0][0]
            name = location[1][0]
            city = u""
            if len(location[0]) > 1:
                city = location[0][1]
            print u"%s-'%s'  '%s' '%s'" % (num, name, url, city)
            num += 1

        seconds = 5
        print "Is that ok? Will wait for %s seconds" % (seconds)
        time.sleep(seconds)

        commands = []


        mqServer = MQServer()
        queue = LTRegisterQueue(mqServer=mqServer)
        sc = ltGeoDataWebScraper()
        #sc.importRC(ltRegisterQueue=queue, max_depth=self.options['max-depth'], throttleMessagesPerSecond=throttleMessagesPerSecond, url=url)

        r = RCCrawledDataExporter()

        for location in list:
            url = location[0][0]
            name = location[1][1]
            commands.append((clearQueue, {"queue" : queue}))
            commands.append((clearGeoData, {}))
            additionalOptions = {}
            if len(location[0]) > 1:
                additionalOptions = location[0][1]
            importRCOptions = {"url": url, "max_depth": 99, 'ltRegisterQueue':queue}
            importRCOptions = dict(importRCOptions, **additionalOptions)
            commands.append((sc.importRC, importRCOptions))

            exportOptions = {"fileName": name}
            exportOptions = dict(exportOptions, **additionalOptions)
            commands.append((r.export, exportOptions))



        print "Starting crawling"

        for command, options in commands:
            command(**options)
            #ExecManagementCommand(commands)

        print "finished. Took %s seconds" % timeMeasurer.ElapsedSeconds()
