from cdb_lt_streets.models import HierarchicalGeoData
from django.core.management.base import BaseCommand
from pjutils.dbUtils import ClearTablesData

class Command(BaseCommand):
    args = '<>'
    help = ''


    def handle(self, *args, **options):
        models = [HierarchicalGeoData]

        ClearTablesData(models)

        print "successfully cleared all data. Street index is empty"


  