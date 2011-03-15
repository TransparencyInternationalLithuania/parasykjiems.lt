import os
from django.core.management.base import BaseCommand
from contactdb.importUtils import createInstitutionType, importInstitutionData

class ImportSources:
    commonPath = os.path.join("cdb_lt", "files", "members")
    LithuanianMPs = os.path.join(commonPath, "parliament members.csv")
    LithuanianMunicipalityMembers = os.path.join(commonPath, "LithuanianMunicipalityMembers.csv")
    LithuanianCivilParishMembers  = os.path.join(commonPath, "LithuanianCivilParishMembers.csv")
    LithuanianSeniunaitijaMembers  = os.path.join(commonPath, "LithuanianSeniunaitijaMembers.csv")

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):

        # create MP
        createInstitutionType(code="mp")
        importInstitutionData(csvFileName=ImportSources.LithuanianMPs, institutionCode = "mp", uniqueKeyStartsFrom=0)

        # create Mayor
        createInstitutionType(code="mayor")
        importInstitutionData(csvFileName=ImportSources.LithuanianMunicipalityMembers, institutionCode = "mayor", uniqueKeyStartsFrom=100000)

        # create Civil Parish
        createInstitutionType(code="civpar")
        importInstitutionData(csvFileName=ImportSources.LithuanianCivilParishMembers, institutionCode = "civpar", uniqueKeyStartsFrom=200000)

        # create Seniunaitija
        createInstitutionType(code="seniunaitija")
        importInstitutionData(csvFileName=ImportSources.LithuanianSeniunaitijaMembers, institutionCode = "seniunaitija", uniqueKeyStartsFrom=300000)


