from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
import types


class Command(BaseCommand):
    args = '<>'
    help = 'Imports data to contact db database'



    def handle(self, *args, **options):

        time = TimeMeasurer()
        imports = ["importConstituencies",
                   "importMPs",
                   "importStreets",
                   ("ltGeoDataImport", {"max-depth" :3}),
                   "importCivilParishMembers",
                   "importMunicipalityMembers",
                   "importSeniunaitija",
                   "importSeniunaitijaMembers"]
        #imports = imports[8:9]

        print "Will import followind data:"
        for i in imports: print i

        print "Starting import"
        for i in imports:
            commandName = i
            commandArgs = {}
            if (isinstance(i, types.TupleType)):
                commandName = i[0]
                commandArgs = i[1]

            print "importing %s" % commandName
            management.call_command(name = commandName, **commandArgs)

        print "finished importing ContactDB. Took %s seconds" % time.ElapsedSeconds()