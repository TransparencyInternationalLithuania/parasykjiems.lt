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

wholeMunicipalityEndings = [u"miesto savivaldybė"]
shortMunicipalityEndings = [u"m. sav."]
allMunicipalityEndings = wholeMunicipalityEndings + shortMunicipalityEndings

  