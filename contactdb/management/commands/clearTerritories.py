from django.core.management.base import BaseCommand
from contactdb.management.commands.clearAll import ClearTablesData
from territories.models import CountryAddresses, InstititutionTerritory

class Command(BaseCommand):
    args = '<>'
    help = 'Clears all information about institution territories'



    def handle(self, *args, **options):
        models = [CountryAddresses,
                  InstititutionTerritory]

        ClearTablesData(models)

        print "Successfully cleared territories data"

