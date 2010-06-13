#!/usr/bin/env python
# -*- coding: utf8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.imp import LithuanianCountyReader, ImportSources
from contactdb.models import CountyStreet, County   
from contactdb.AdressParser import AddressParser
from datetime import datetime

import os

class Command(BaseCommand):
    args = '<number of elelctoral districts (sub-units of counties) to import streets into db>'
    help = """Imports into database all Lithuanian streets and relates to Lithuanian Counties
It is safe to run this command more than once. Before inserting new electoral districts streets, previous streets for same electoral district will be deleted
Examples:
importStreets 5 - will import streets for first 5 Election Districts. If run repeatedly, result will be the same, except that manually entered data will be deleted
importStreets 5:8 - will import streets for counties from 5 to 8 county inclusive  """

    def deleteElectionDistrictIfExists(self, electionDistrict):
        # not sure how to format this line in Python
        # method chaining is nice, but how to format this nicely?
        CountyStreet.objects.filter(electionDistrict = electionDistrict).delete()
        
    @transaction.commit_on_success


    def getLocations(self, fromPrint, toPrint):
        pass
    

    @transaction.commit_on_success    
    def handle(self, *args, **options):
        allRecords = os.getcwd() + ImportSources.LithuanianCounties
        file = open(allRecords, "r")

        fromPrint = 0
        toPrint = 9999999

        if len(args) > 0:
            if (args[0].find(":") > 0):
                split = args[0].split(':')
                fromPrint = int(split[0])
                toPrint = int(split[1])
            else:
                toPrint = int(args[0])

        streetParser = AddressParser() 

        count = 0
        imported = 0
        totalNumberOfStreets = 0
        aggregator = LithuanianCountyReader(file)


        start = datetime.now()
        for location in aggregator.getLocations():


            if (count + 1 > toPrint):
                break
            count += 1
            if (count + 1 <= fromPrint):
                continue
                

            
            self.deleteElectionDistrictIfExists(location.ElectionDistrict)
            county = County.objects.get(nr = location.County.nr)

            imported += 1
            numberOfStreets = 0
            for street in streetParser.GetAddresses(location.Addresses):
                countyStreet = CountyStreet()
                countyStreet.county = county
                countyStreet.district = location.District
                countyStreet.city = street.cityName
                countyStreet.street = street.streetName
                countyStreet.electionDistrict = location.ElectionDistrict
                countyStreet.save()
                numberOfStreets += 1

            totalNumberOfStreets += numberOfStreets
            now = datetime.now()
            seconds = (now - start).seconds
            if (seconds == 0):
                rate = "unknown"
            else:
                rate = str(totalNumberOfStreets / seconds)
            print (u"%d: saved County '%s %d', \nElectoral District '%s' streets (%d). \nTotal streets so far %d" % (count, county.name, county.nr, location.ElectionDistrict, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print "inserting at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)
            print "\n\n"



        print "succesfully imported %d counties, total %d streets" % (imported, totalNumberOfStreets)