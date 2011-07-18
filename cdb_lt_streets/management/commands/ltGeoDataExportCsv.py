#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from optparse import make_option
from types import IntType
from django.core.management.base import BaseCommand
from django.core import management
from cdb_lt.management.commands.downloadTerritories import territoriesCsvFormat
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_streets.models import HierarchicalGeoData
from distutils import dir_util
import os
import logging

logger = logging.getLogger(__name__)

class RCCrawledDataExporter(object):
    def __init__(self):
        self.parentCache = {}

    def getObject(self, object):
        if self.parentCache.has_key(object.id):
            return self.parentCache[object.id]

        self.parentCache[object.id] = object
        return object


    def getParentValues(self, obj):
        values = {}
        while obj is not None:
            obj = self.getObject(obj)
            values[obj.type] = obj.name

            if obj.type == HierarchicalGeoData.HierarchicalGeoDataType.City:
                values[obj.type] = obj.name
                values["citygenitive"] = obj.name_genitive
            obj = obj.parent
        return values


    def toCsvDictFromDict(self, d):
        for k in d.iterkeys():
            if d[k] is None:
                continue
            if type(d[k]) is not IntType:
                d[k] = d[k].replace("\n", " ")
                d[k] = d[k].strip()
                d[k] = d[k].encode("utf-8")
        return d

    def writeToFile(self, values):
        v = self.toCsvDictFromDict(values)
        self.file.writerow(v)


    def export(self, fileName, city = None, insertCivilParish = None):
        self.parentCache = {}
        cityMode = city is not None and city.strip() != ""
        elapsedTime = TimeMeasurer()
        logger.info("Writing contents to %s" % fileName)
        logger.info("using city mode: %s" % cityMode)


        dir_util.mkpath(os.path.dirname(fileName))
        #self.file = open(fileName, 'w')
        #self.writeToFile(territoriesCsvFormat)
        self.file = csv.DictWriter(open(fileName, "wb"), territoriesCsvFormat)
        headers = dict( (n,n) for n in territoriesCsvFormat )
        self.file.writerow(headers)



        allIds = HierarchicalGeoData.objects.values_list('id', flat = True).order_by('name')
        count = 0

        for id in allIds:

            childrenCount = len(HierarchicalGeoData.objects.all().filter(parent__id = id))
            if childrenCount != 0:
                print "id %s has %s children, skipping" % (id, childrenCount)
                continue
            count += 1
            print "id %s has %s children" % (id, childrenCount)
            obj = HierarchicalGeoData.objects.all().filter(id = id)[0]
            parent_values = self.getParentValues(obj)
            parent_values["id"] = count


            if cityMode == True:
                parent_values["citygenitive"] = parent_values["city"]
                parent_values["city"] = city


            self.writeToFile(parent_values)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, total %s lines" % count


class Command(BaseCommand):
    args = '<>'
    help = """Exports data from HierarchicalGeoData to csv file"""

    option_list = BaseCommand.option_list + (
        make_option('-f', '--file',
            dest='file',
            metavar="file",
            default = "geoData.csv",
            help='Specify a file name where to save extracted data'),
         make_option('-c', '--city',
            dest='city',
            metavar="city",
            default = "",
            help="""If this is not empty string, then this will be treated as special case. The case is when parsing a city streets. For example
Kaunas city streets are here: http://www.registrucentras.lt/adr/p/index.php?gyv_id=6    What is different is that it does not have a civil parish written
in the location position, that is 'LIETUVOS RESPUBLIKA / Kauno apskr. / Kauno m. sav. / <this part is missing>/Kauno m.'
Also, the city name is only in genitive form, no nominative form. So when exporting a civil parish will be empty, and city param will be a nominative form of city"""),
        make_option('-i', '--insertCivilParish',
            dest='insertCivilParish',
            metavar="insertCivilParish",
            default = "True",
            help="""Used only in conjuction with --city option.  If this is True, then it is treated that a CivilParish is missing directly before city, and thus it will be
inserterted as empty. If False, then this will not be inserted. See RegisterCenterPageLocations.allStreets variable to see which RegisterCenter page locations require this"""),
        )

    def handle(self, *args, **options):
        fileName = options['file']
        city = options['city']
        city = unicode(city, 'utf-8')
        insertCivilParish = bool(options['insertCivilParish'])

        r = RCCrawledDataExporter()
        r.export(fileName = fileName, city = city, insertCivilParish = insertCivilParish)
