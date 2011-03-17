import os
from django.core.management.base import BaseCommand
from contactdb.importUtils import createInstitutionType, importInstitutionData, readRow

class ImportSources:
    commonPath = os.path.join("cdb_lt", "files", "members")
    LithuanianMPs = os.path.join(commonPath, "parliament members.csv")
    LithuanianMunicipalityMembers = os.path.join(commonPath, "LithuanianMunicipalityMembers.csv")
    LithuanianCivilParishMembers  = os.path.join(commonPath, "LithuanianCivilParishMembers.csv")
    LithuanianSeniunaitijaMembers  = os.path.join(commonPath, "LithuanianSeniunaitijaMembers.csv")


def makeCivilParishInstitutionName(csvRow):
    municipality = readRow(csvRow, "municipality")
    civilParish = readRow(csvRow, "civilparish")
    return "%s %s" % (municipality, civilParish)


def makeSeniunaitijaInstitutionName(csvRow):
    municipality = readRow(csvRow, "municipality")
    civilParish = readRow(csvRow, "civilparish")
    seniunaitija = readRow(csvRow, "seniunaitija")
    return "%s %s %s" % (municipality, civilParish, seniunaitija)

def cityNameGetterGenitive(csvRow):
    """ Lithuanian streets can be defined in two forms. However, only genitive is used as primary key, while users
    use both interchangeably"""
    return readRow(csvRow, "city_genitive")

InstitutionMunicipalityCode = "mayor"

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):

        # create MP
        createInstitutionType(code="mp")
        importInstitutionData(csvFileName=ImportSources.LithuanianMPs, institutionCode = "mp", uniqueKeyStartsFrom=0)

        # create Mayor
        createInstitutionType(code="mayor")
        importInstitutionData(csvFileName=ImportSources.LithuanianMunicipalityMembers, institutionCode = InstitutionMunicipalityCode, uniqueKeyStartsFrom=100000)

        # create Civil Parish
        createInstitutionType(code="civpar")
        importInstitutionData(csvFileName=ImportSources.LithuanianCivilParishMembers, institutionCode = "civpar", institutionNameGetter=makeCivilParishInstitutionName, uniqueKeyStartsFrom=200000)

        # create Seniunaitija
        createInstitutionType(code="seniunaitija")
        importInstitutionData(csvFileName=ImportSources.LithuanianSeniunaitijaMembers, institutionCode = "seniunaitija", institutionNameGetter=makeSeniunaitijaInstitutionName, uniqueKeyStartsFrom=300000)


