from django.core.management.base import BaseCommand
from contactdb.models import Person, PersonPosition, InstitutionType, Institution
from pjutils.dbUtils import ClearTablesData

class Command(BaseCommand):
    args = '<>'
    help = 'Clears all information about persons and institutions'



    def handle(self, *args, **options):
        models = [PersonPosition,
                  Institution,
                InstitutionType,
                Person]

        ClearTablesData(models)

        print "Successfully cleared members data"

