from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import HierarchicalGeoData
from contactdb.imp import ImportSources
import csv
from pjutils.uniconsole import *


class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""

    def createIfNotNull(self, name, type, parent = None):
        try:
            existing = HierarchicalGeoData.objects.all().filter(name = name) \
                .filter(type = type)
            if (parent is None):
                existing = existing.filter(parent__isnull = True)
            else:
                existing = existing.filter(parent = parent)
            existing = existing[0:1].get()
            print u"object %s %s exists, skipping" % (name, type)
            return existing
        except HierarchicalGeoData.DoesNotExist:
            self.count += 1
            print u"creating %s %s" % (name, type)
            newObject = HierarchicalGeoData(name = name, type = type, parent = parent)
            newObject.save()
            return newObject

    def handle(self, *args, **options):
        fileName = ImportSources.LithuanianStreetIndex
        print u"Import street index data from csv file %s" % fileName
        ImportSources.EsnureExists(ImportSources.LithuanianStreetIndex)

        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")

        self.count = 0

        for row in self.dictReader:
            id = unicode(row["id"].strip(), 'utf-8')
            country = unicode(row["country"].strip(), 'utf-8')
            county = unicode(row["county"].strip(), 'utf-8')
            municipality = unicode(row["municipality"].strip(), 'utf-8')
            civilParish = unicode(row["civilparish"].strip(), 'utf-8')
            city = unicode(row["city"].strip(), 'utf-8')
            street = unicode(row["street"].strip(), 'utf-8')

            parent = self.createIfNotNull(country, HierarchicalGeoData.HierarchicalGeoDataType.Country)
            parent = self.createIfNotNull(county, HierarchicalGeoData.HierarchicalGeoDataType.Country, parent = parent)
            parent = self.createIfNotNull(municipality, HierarchicalGeoData.HierarchicalGeoDataType.Country, parent = parent)
            parent = self.createIfNotNull(civilParish, HierarchicalGeoData.HierarchicalGeoDataType.Country, parent = parent)
            parent = self.createIfNotNull(street, HierarchicalGeoData.HierarchicalGeoDataType.Country, parent = parent)


        print u"finished, written total %s lines" % self.count

