#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import HierarchicalGeoData
from distutils import dir_util
import os
import logging

logger = logging.getLogger(__name__)

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
        )

    def __init__(self):
        self.parentCache = {}

    def getParentValues(self, obj):
        values = []
        while (obj.parent is not None):
            parent = obj.parent
            parentId = parent.id
            if (self.parentCache.has_key(parentId)):
                parent = self.parentCache[parentId]
            else:
                self.parentCache[parentId] = parent

            if (parent.type == HierarchicalGeoData.HierarchicalGeoDataType.City):
                values.append(parent.name_genitive)
            values.append(parent.name)
            obj = parent
        values.reverse()
        return values

    def writeToFile(self, values):
        delimiter = u", "
        v = []
        for val in values:
            if val is None:
                val = u""
            v.append(val)
        values = v
        valuesStr = u"%s%s%s" % (values[0], delimiter, delimiter.join(values[1:]))
        valuesStr = valuesStr.encode('UTF-8')
        self.file.write(valuesStr)
        self.file.write("\n")

    def handle(self, *args, **options):

        elapsedTime = TimeMeasurer()
        fileName = options['file']
        self.city = options['city']
        self.cityMode = self.city is not None and self.city.strip() != ""
        logger.info("Writing contents to %s" % fileName)
        logger.info("using city mode: %s" % self.cityMode)


        dir_util.mkpath(os.path.dirname(fileName))
        self.file = open(fileName, 'w')

        self.writeToFile([u"Id",
                          HierarchicalGeoData.HierarchicalGeoDataType.Country,
                          HierarchicalGeoData.HierarchicalGeoDataType.County,
                          HierarchicalGeoData.HierarchicalGeoDataType.Municipality,
                          HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                          HierarchicalGeoData.HierarchicalGeoDataType.City,
                          u"City_genitive",
                          HierarchicalGeoData.HierarchicalGeoDataType.Street,])

        allIds = HierarchicalGeoData.objects.values_list('id', flat = True).order_by('id')
        count = 0

        for id in allIds:

            childrenCount = len(HierarchicalGeoData.objects.all().filter(parent__id = id))
            if (childrenCount != 0):
                print "id %s has %s children, skipping" % (id, childrenCount)
                continue
            count += 1
            print "id %s has %s children" % (id, childrenCount)
            obj = HierarchicalGeoData.objects.all().filter(id = id)[0]
            parent_values = self.getParentValues(obj)

            finalValues = [count]
            for pv in parent_values:
                finalValues.append(pv)
            finalValues.append(obj.name)

            if (self.cityMode):
                finalValues.insert(len(finalValues) - 2, u"")
                finalValues.insert(len(finalValues) -2, self.city)

            if (self.cityMode == False):
                if (obj.type == HierarchicalGeoData.HierarchicalGeoDataType.City):
                    finalValues.append(obj.name_genitive)
            self.writeToFile(finalValues)

        self.file.close()
        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, total %s lines" % count

