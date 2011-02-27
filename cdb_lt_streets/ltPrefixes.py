#!/usr/bin/env python
# -*- coding: utf-8 -*-

# here we define all standard lithuanian street and city names, and
# their short forms also


shortCityEndings = [u"mstl.", u"vs.", u"m.", u"k."]
wholeCityEndings = [u"miestelis", u"viensėdis", u"miestas", u"kaimas"]
allCityEndings = wholeCityEndings + shortCityEndings

wholeStreetEndings = [u"skersgatvis", u"kelias", u"plentas", u"prospektas",
                    u"alėja", u"gatvė", u"aikštė", u"takas"]
shortStreetEndings = [u"skg.", u"kel.", u"pl.", u"pr.", u"al.", u"g.", u"a.", u"tak."]
allStreetEndings = wholeStreetEndings + shortStreetEndings

shortCivilParishEndings = [u"sen."]
wholeCivilParishEndings = [u"seniūnija"]
allCivilParishEndings = wholeCivilParishEndings + shortCivilParishEndings

wholeMunicipalityEndings = [u"miesto savivaldybė", u"rajono savivaldybė"]
shortMunicipalityEndings = [u"m. sav.", u"r. sav."]
allMunicipalityEndings = wholeMunicipalityEndings + shortMunicipalityEndings


zippedStreetPrefixes = zip(shortStreetEndings, wholeStreetEndings)
zippedCityPrefixes = zip(shortCityEndings, wholeCityEndings)

def extractStreetEndingForm(street):
    """ for example, from string "MyStreet g." will return "g." """
    if street is None:
        return u""
    if street == u"":
        return street
    for prefix in allStreetEndings:
        index = street.find(prefix)
        if index >= 0:
            return prefix

def changeStreetFromShortToLongForm(street):
    """ Changes for example from "Respublikos g." to "Respublikos gatvė" """
    if street is None:
        return None
    if street == "":
        return ""
    for shortPrefix, longPrefix in zippedStreetPrefixes:
        index = street.find(shortPrefix)
        if index >= 0:
            expanded = "%s%s" % (street[0:index], longPrefix)
            return expanded
    return street

def changeCityFromShortToLongForm(city):
    """ Changes for example from "Balbieriškių k." to "Balbieriškių kaimas" """
    if (city is None):
        return None
    if (city == ""):
        return ""
    for shortPrefix, longPrefix in zippedCityPrefixes:
        index = city.find(shortPrefix)
        if (index >= 0):
            expanded = "%s%s" % (city[0:index], longPrefix)
            return expanded
    return city

def removeGenericPartFromStreet(street):
    if (street is None):
        return ""
    for e in allStreetEndings:
        if street.endswith(e):
            street = street.replace(e, u"")
    return street.strip()

def removeGenericPartFromCity(city):
    for e in allCityEndings:
        if city.endswith(e):
            city = city.replace(e, u"")
    return city.strip()


def removeGenericPartFromMunicipality(municipality):
    for e in allMunicipalityEndings:
        if municipality.endswith(e):
            municipality = municipality.replace(e, u"")

    other = [u"savivaldybė", u"m.", u"r.", "sav."]
    for e in other:
        if municipality.find(e) >= 0:
            municipality = municipality.replace(e, u"")
    return municipality.strip()

def containsCivilParishEnding(civilParish):
    for e in allCivilParishEndings:
        if civilParish.find(e) >= 0:
            return True
    return False

def containsStreet(str):
    for ending in allStreetEndings:
        if str.find(ending) >= 0:
            return True
    return False

def containsMunicipalityEnding(municipality):
    for e in allMunicipalityEndings:
        if municipality.find(e) >= 0:
            return True
    return False