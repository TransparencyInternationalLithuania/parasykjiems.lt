from contactdb.management.commands.clearAll import ClearTablesData
from cdb_lt_streets.models import HierarchicalGeoData
from django.core.management.base import BaseCommand
from cdb_lt_civilparish.models import CivilParish, CivilParishStreet, CivilParishMember

class Command(BaseCommand):
    args = '<>'
    help = ''


    def handle(self, *args, **options):
        models = [CivilParish,
                  CivilParishMember,
                  CivilParishStreet]

        ClearTablesData(models)

        print "successfully cleared all data. Civil parish street index is empty"
