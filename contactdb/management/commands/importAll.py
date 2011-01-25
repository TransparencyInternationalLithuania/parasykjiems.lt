from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from pjutils.djangocommands import ExecManagementCommand

class Command(BaseCommand):
    args = '<>'
    help = 'Imports data to contact db database'



    def handle(self, *args, **options):

        time = TimeMeasurer()
        imports = [
                   "importConstituencies",   # LT MP data
                   "importMPs",
                   "importCivilParish",      # LT CivilParish data
                   "importCivilParishMembers",
                   "importMunicipality",     # LT Municipality data
                   "importMunicipalityMembers",
                   "importSeniunaitija",     # LT Seniunaitija data
                   "importSeniunaitijaMembers"]

        print "Will import following data:"
        for i in imports:
            print i

        print u"Starting import"

        ExecManagementCommand(imports)

        print u"finished importing ContactDB. Took %s seconds" % time.ElapsedSeconds()
