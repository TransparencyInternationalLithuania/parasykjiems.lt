#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from territories.territoryImportUtils import importCountryData

class ltGeoDataSources_Country:

    commonStreetPath = os.path.join("cdb_lt", "files", "territory", "city")

    addressesInCities = [
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Alytus City", os.path.join(commonStreetPath, "cdb_lt_street_index_Alytus_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Kaunas City", os.path.join(commonStreetPath, "cdb_lt_street_index_Kaunas_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Klaipeda City", os.path.join(commonStreetPath, "cdb_lt_street_index_Klaipeda_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Marijampole City", os.path.join(commonStreetPath, "cdb_lt_street_index_Marijampole_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Panevezio City", os.path.join(commonStreetPath, "cdb_lt_street_index_Panevezys_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Siauliu City", os.path.join(commonStreetPath, "cdb_lt_street_index_Siauliai_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Taurage City", os.path.join(commonStreetPath, "cdb_lt_street_index_Taurage_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Telsiu City", os.path.join(commonStreetPath, "cdb_lt_street_index_Telsiai_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Utena City", os.path.join(commonStreetPath, "cdb_lt_street_index_Utena_city.csv")),
        ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Vilnius City", os.path.join(commonStreetPath, "cdb_lt_street_index_Vilnius_city.csv")),
    ]

    commonPath = os.path.join("cdb_lt", "files", "territory", "municipality")
    addressesInMunicipalities = [
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Alytaus apskr.", os.path.join(commonPath, "cdb_lt_street_index_alytaus_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Kauno apskr.", os.path.join(commonPath, "cdb_lt_street_index_kaunas_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Klaipėdos apskr.", os.path.join(commonPath, "cdb_lt_street_index_klaipeda_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Marijampolės apskr.", os.path.join(commonPath, "cdb_lt_street_index_marijampole_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Panevėžio apskr.", os.path.join(commonPath, "cdb_lt_street_index_panevezys_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Šiaulių apskr.", os.path.join(commonPath, "cdb_lt_street_index_siauliai_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Tauragės apskr.", os.path.join(commonPath, "cdb_lt_street_index_taurge_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Telšių apskr.", os.path.join(commonPath, "cdb_lt_street_index_telsiai_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Utenos apskr.", os.path.join(commonPath, "cdb_lt_street_index_utena_apskritis.csv")),
                    ("Contact DB LT Street Index - LIETUVOS RESPUBLIKA / Vilniaus apskr.", os.path.join(commonPath, "cdb_lt_street_index_vilnius_apskritis.csv"))
    ]

    """ A complete Lithuanian street source: cities plus municipalities"""
    LithuanianStreetIndexes = addressesInMunicipalities + addressesInCities

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):

        # create MP
        fileNames = [f[1] for f in ltGeoDataSources_Country.LithuanianStreetIndexes]
        importCountryData(csvFileNames=fileNames)


