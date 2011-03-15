import os
from django.core.management.base import BaseCommand
from contactdb.importUtils import createInstitutionType, importInstitutionData

class ImportSources:
    commonPath = os.path.join("cdb_lt", "files", "members")
    LithuanianMPs = os.path.join(commonPath, "parliament members.csv")

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):

        # create MP

        createInstitutionType(code="mp")
        importInstitutionData(csvFileName=ImportSources.LithuanianMPs, institutionCode = "mp")


        # create Mayor

        # create Civil Parish

        # create Seniunaitija


