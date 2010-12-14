from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from importAll import ExecManagementCommand
import types

class Command(BaseCommand):
    args = '<>'
    help = 'Imports initial / automatically unchangeable data. Such data is constituencies and constituency streets for LT data'

    def handle(self, *args, **options):

        time = TimeMeasurer()
        #"ltGeoDataDownloadDocs",
        imports = ["ltStreetIndexImport",     # LT street index
                   "importConstituencies",   # LT MP data
                   "importMPs",
                   "importStreets",
                   "importCivilParish",      # LT CivilParish data
                   "importCivilParishMembers",
                   "importCivilParishStreets",
                   "importMunicipality",     # LT Municipality data
                   "importMunicipalityMembers",
                   "importSeniunaitija",     # LT Seniunaitija data
                   "importSeniunaitijaMembers",
                   "importSeniunaitijaStreets"]
        #imports = imports[8:9]

        print "Will import following data:"
        for i in imports:
            print i

        print "Starting import"

        ExecManagementCommand(imports)

        print "finished importing ContactDB. Took %s seconds" % time.ElapsedSeconds()
