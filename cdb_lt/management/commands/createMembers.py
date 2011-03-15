import os
from django.core.management.base import BaseCommand
from contactdb.importUtils import createInstitutionType, importInstitutionData

class ImportSources:
    commonPath = os.path.join("cdb_lt", "files", "members")
    LithuanianMPs = os.path.join(commonPath, "parliament members.csv")
    LithuanianMunicipalityMembers = os.path.join(commonPath, "LithuanianMunicipalityMembers.csv")
    LithuanianCivilParishes  = os.path.join(commonPath, "LithuanianCivilParishes.csv")

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):

        # create MP

        createInstitutionType(code="mp")
        importInstitutionData(csvFileName=ImportSources.LithuanianMPs, institutionCode = "mp", uniqueKeyStartsFrom=0)


        # create Mayor
        createInstitutionType(code="mayor")
        importInstitutionData(csvFileName=ImportSources.LithuanianMunicipalityMembers, institutionCode = "mayor", uniqueKeyStartsFrom=1000)

        # create Civil Parish
        #createInstitutionType(code="civpar")
        #importInstitutionData(csvFileName=ImportSources.LithuanianCivilParishes, institutionCode = "civpar", uniqueKeyStartsFrom=2000)

        # create Seniunaitija


