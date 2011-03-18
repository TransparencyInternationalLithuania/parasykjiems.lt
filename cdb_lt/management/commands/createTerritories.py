#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from cdb_lt.civilParishKaunasStreetReader import civilParishKaunasStreetReader
from cdb_lt.civilParishStreetReader import civilParishStreetReader
from cdb_lt.civilParishVilniusStreetReader import civilParishVilniusStreetReader
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, cityNameGetterGenitive, InstitutionMunicipalityCode
from cdb_lt.management.commands.importSources import ltGeoDataSources_Institution, ltGeoDataSources_Country
from cdb_lt.mpStreetReader import mpStreetReader
from cdb_lt.municipalityStreetReader import municipalityStreetReader
from cdb_lt.seniunaitijaTerritoryReader import seniunaitijaStreetReader
from territories.models import LithuanianCases
from cdb_lt.ltData import MunicipalityCases
from territories.territoryImportUtils import importCountryData, importInstitutionTerritoryYielder


def importCases():
    print "Will import LithuanianCases for municipalities"

    all = LithuanianCases.objects.all().filter(institutionType=LithuanianCases.Type.Municipality)
    d = {}
    for c in all:
        d[c.nominative] = c
    
    for key, data in MunicipalityCases.iteritems():
        if d.has_key(key):
            continue
        case = LithuanianCases()
        case.nominative = key
        case.genitive = data
        case.institutionType = LithuanianCases.Type.Municipality
        case.save()
    print "finished"

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):


        importCases()

        # create Country data
        fileNames = [f[1] for f in ltGeoDataSources_Country.LithuanianAddresses]
        importCountryData(csvFileNames=fileNames)

        # create addresses for civilParish
        fileNames = [f[1] for f in ltGeoDataSources_Institution.civilParishAddresses]
        importInstitutionTerritoryYielder(addressYielder=civilParishStreetReader(csvFileNames=fileNames, institutionNameGetter=makeCivilParishInstitutionName, cityNameGetter = cityNameGetterGenitive), institutionCode = "civpar")

        importInstitutionTerritoryYielder(addressYielder=civilParishVilniusStreetReader(), institutionCode = "civpar")

        importInstitutionTerritoryYielder(addressYielder=civilParishKaunasStreetReader(), institutionCode = "civpar")


        # create addresses for seniunaitija
        importInstitutionTerritoryYielder(addressYielder=seniunaitijaStreetReader(), institutionCode = "seniunaitija")

        # create Municipality data
        importInstitutionTerritoryYielder(addressYielder=municipalityStreetReader(), institutionCode = InstitutionMunicipalityCode)

        # create MP data
        importInstitutionTerritoryYielder(addressYielder=mpStreetReader(), institutionCode = "mp")

        