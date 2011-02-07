from contactdb.management.commands.clearAll import ClearTablesData
from cdb_lt_streets.models import HierarchicalGeoData
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = '<>'
    help = ''


    def handle(self, *args, **options):
        models = [HierarchicalGeoData]

        ClearTablesData(models)

        print "successfully cleared all data. Street index is empty"


  