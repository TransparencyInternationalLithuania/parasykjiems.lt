#!/usr/bin/env python
# -*- coding: utf8 -*-
from django.core.management.base import BaseCommand
from contactdb.imp import LithuanianCountyReader, ImportSources
from contactdb.models import CountyStreet
from contactdb.AdressParser import AddressParser
import os

class Command(BaseCommand):
    args = '<number of elelctoral districts (sub-units of counties) to import streets into db>'
    help = 'Imports into database all Lithuanian streets and relates to Lithuanian Counties'

    def handle(self, *args, **options):
        allRecords = os.getcwd() + ImportSources.LithuanianCounties
        file = open(allRecords, "r")

        numberToPrint = 9999
        if len(args) > 0:
            numberToPrint = int(args[0])

        streetParser = AddressParser() 

        count = 0

        totalNumberOfStreets = 0
        aggregator = LithuanianCountyReader(file)
        for location in aggregator.getLocations():

            countyStreet = CountyStreet()

            county = County.objects.get(nr = location.county.nr)


            numberOfStreets = 0
            for street in streetParser.GetAddresses(location.Addresses):
                countyStreet.county = county
                countyStreet.district = location.District
                countyStreet.city = street.streetName
                countyStreet.street = street.streetName
                countyStreet.save()
                numberOfStreets += 1

            totalNumberOfStreets += numberOfStreets
            count += 1
            if (count >= numberToPrint):
                break;
            print "saved County %s %d streets (%d). Total streets so far %d" % (c.name, c.nr, numberOfStreets, totalNumberOfStreets)
        print "succesfully imported %d counties, total %d streets" % (count, totalNumberOfStreets)