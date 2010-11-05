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


class Command(BaseCommand):
    args = '<>'
    help = """Exports data from HierarchicalGeoData to csv file"""

    option_list = BaseCommand.option_list + (
        make_option('-f', '--file',
            dest='file',
            metavar="file",
            default = "geoData.csv",
            help='Specify a file name where to save extracted data'),
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
        valuesStr = "%s%s%s" % (values[0], delimiter, delimiter.join(values[1:]))
        valuesStr = valuesStr.encode('UTF-8')
        self.file.write(valuesStr)
        self.file.write("\n")

    def handle(self, *args, **options):

        elapsedTime = TimeMeasurer()
        fileName = options['file']
        print "Writing contents to %s" % fileName

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
            if (obj.type == HierarchicalGeoData.HierarchicalGeoDataType.City):
                finalValues.append(obj.name_genitive)
            self.writeToFile(finalValues)

        self.file.close()
        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, total %s lines" % count

