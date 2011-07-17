from django.core.management.base import BaseCommand
from pjutils.dbUtils import ClearTablesData
from territories.models import CountryAddress, InstitutionTerritory

class Command(BaseCommand):
    args = '<>'
    help = 'Clears all information about institution territories'



    def handle(self, *args, **options):
        models = [CountryAddress,
                  InstitutionTerritory]

        ClearTablesData(models)

        print "Successfully cleared territories data"

