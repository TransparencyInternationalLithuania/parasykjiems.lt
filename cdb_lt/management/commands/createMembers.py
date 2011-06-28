#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from cdb_lt.management.commands.importSources import ImportSourcesMembers
from contactdb.importUtils import createInstitutionType, importInstitutionData, readRow

def makeCivilParishInstitutionName(csvRow):
    municipality = readRow(csvRow, "municipality")
    civilParish = readRow(csvRow, "civilparish")
    return "%s %s" % (municipality, civilParish)


def makeSeniunaitijaInstitutionName(csvRow):
    municipality = readRow(csvRow, "municipality")
    civilParish = readRow(csvRow, "civilparish")
    seniunaitija = readRow(csvRow, "seniunaitija")
    return "%s %s %s" % (municipality, civilParish, seniunaitija)

def makeMunicipalityInstitutionName(csvRow):
    municipality = readRow(csvRow, "municipality")
    return "%s" % municipality

def cityNameGetterGenitive(csvRow):
    """ Lithuanian streets can be defined in two forms. However, only genitive is used as primary key, while users
    use both interchangeably"""
    return readRow(csvRow, "city_genitive")

InstitutionMunicipalityCode = u"Mayor"
InstitutionParliamentMember = u"Member of parliament"
InstitutionCivilparishMembers = u"Civil parish member"
InstitutionSeniunaitijaMembers = u"Seniūnas"

def loadInstitutionDescriptions():
    institutionDescriptions = {
            InstitutionParliamentMember:{
                "InstitutionPosition" : u"Seimo narys",
                "InstitutionResponsibility" : u"Atsakingas už įstatymų leidybą, įstatymu numatytų Lietuvos valstybės institucijų vadovų skyrimą ir atleidimą iš pareigų, valstybės biudžeto tvirtinimą, Lietuvos Respublikos Vyriausybės veiklos priežiūrą."
            },
            InstitutionMunicipalityCode:{
                "InstitutionPosition" : u"Meras",
                "InstitutionResponsibility" : u"Užtikrina, kad savivaldybės gyventojai turėtų galimybę įsitraukti į vietos reikalų tvarkymą, kad būtų tobulinamas savivaldybės tarybos sprendimų priėmimas ir savivaldybės tarybos komitetų veikla."
            },
            InstitutionCivilparishMembers:{
                "InstitutionPosition" : u"Seniūnas",
                "InstitutionResponsibility" : u"Atlieka seniūnijos vidaus administravimą, prižiūri viešųjų paslaugų teikimą, neatlygintinai atlieka tam tikras notarines funkcijas, konsultuoja seniūnijai priskirtos teritorijos gyventojus, pagal kompetenciją gali surašyti administracinių teisės pažeidimų protokolus, nagrinėti administracinių teisės pažeidimų bylas, gali registruoti mirtis, išduoda leidimus laidoti."
            },
            InstitutionSeniunaitijaMembers:{
                "InstitutionPosition" : u"Seniūnaitis",
                "InstitutionResponsibility" : u"Skatina seniūnaitijos gyventojus prižiūrėti gyvenamosios vietovės teritoriją, plėtoti ir organizuoti vietovės kultūrinį ir sportinį gyvenimą, turi teisę gauti ir teikia informaciją apie savivaldybės institucijų funkcijas, jų darbo laiką ir darbo tvarką, gali atstovauti seniūnaitijos gyventojams savivaldybės tarybos posėdžiuose."
            }

        }
    return institutionDescriptions

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):

        # create MP
        createInstitutionType(code=InstitutionParliamentMember)
        importInstitutionData(csvFileName=ImportSourcesMembers.LithuanianMPs, institutionCode = InstitutionParliamentMember, uniqueKeyStartsFrom=0)

        # create Mayor
        createInstitutionType(code=InstitutionMunicipalityCode)
        importInstitutionData(csvFileName=ImportSourcesMembers.LithuanianMunicipalityMembers, institutionCode = InstitutionMunicipalityCode, uniqueKeyStartsFrom=100000)

        # create Civil Parish
        createInstitutionType(code=InstitutionCivilparishMembers)
        importInstitutionData(csvFileName=ImportSourcesMembers.LithuanianCivilParishMembers, institutionCode = InstitutionCivilparishMembers, institutionNameGetter=makeCivilParishInstitutionName, uniqueKeyStartsFrom=200000)

        # create Seniunaitija
        createInstitutionType(code=InstitutionSeniunaitijaMembers)
        importInstitutionData(csvFileName=ImportSourcesMembers.LithuanianSeniunaitijaMembers, institutionCode = InstitutionSeniunaitijaMembers, institutionNameGetter=makeSeniunaitijaInstitutionName, uniqueKeyStartsFrom=300000)