from cdb_lt_streets.models import HierarchicalGeoData
from django.core.management.base import BaseCommand
from pjutils.dbUtils import ClearTablesData


def clearGeoData():
    models = [HierarchicalGeoData]
    ClearTablesData(models)
    print "successfully cleared all data. Street index is empty"

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        clearGeoData()
