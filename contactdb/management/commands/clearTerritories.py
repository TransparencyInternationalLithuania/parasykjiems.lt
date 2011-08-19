from django.core.management.base import BaseCommand
from pjutils.dbUtils import ClearTablesData
from territories.models import CountryAddresses, InstitutionTerritory

class Command(BaseCommand):
    args = '<>'
    help = 'Clears all information about institution territories'



    def handle(self, *args, **options):
        models = [CountryAddresses,
                  InstitutionTerritory]

        ClearTablesData(models)

        print "Successfully cleared territories data"

