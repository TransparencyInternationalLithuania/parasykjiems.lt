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

wholeMunicipalityEndings = [u"miesto savivaldybė", u"rajono savivaldybė"]
shortMunicipalityEndings = [u"m. sav.", u"r. sav."]
allMunicipalityEndings = wholeMunicipalityEndings + shortMunicipalityEndings


zippedStreetPrefixes = zip(shortStreetEndings, wholeStreetEndings)
zippedCityPrefixes = zip(shortCityEndings, wholeCityEndings)

def changeStreetFromShortToLongForm(street):
    """ Changes for example from "Respublikos g." to "Respublikos gatvė" """
    if (street is None):
        return None
    if (street == ""):
        return ""
    for shortPrefix, longPrefix in zippedStreetPrefixes:
        index = street.find(shortPrefix)
        if (index >= 0):
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