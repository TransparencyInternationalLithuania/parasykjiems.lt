from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import HierarchicalGeoData


class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""

    def getParentValues(self, obj):
        values = []
        while (obj.parent is not None):
            values.append(obj.parent.name)
            obj = obj.parent
        values.reverse()
        return values

    def writeToFile(self, values):
        valuesStr = "%s\t%s" % (values[0], u"\t".join(values[1:]))
        valuesStr = valuesStr.encode('UTF-8')
        self.file.write(valuesStr)
        self.file.write("\n")

    def handle(self, *args, **options):

        fileName = u"geoData.csv"
        print u"Writing contents to %s" % fileName
        self.file = open(fileName, 'w')

        self.writeToFile([u"Id",
                          HierarchicalGeoData.HierarchicalGeoDataType.Country,
                          HierarchicalGeoData.HierarchicalGeoDataType.County,
                          HierarchicalGeoData.HierarchicalGeoDataType.Municipality,
                          HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                          HierarchicalGeoData.HierarchicalGeoDataType.City,
                          HierarchicalGeoData.HierarchicalGeoDataType.Street])

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
            self.writeToFile(finalValues)

        self.file.close()
        print u"finished, total %s lines" % count

