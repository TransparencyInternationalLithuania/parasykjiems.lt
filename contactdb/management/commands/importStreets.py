#!/usr/bin/env python
# -*- coding: utf8 -*-
from django.core.management.base import BaseCommand
from contactdb.imp import LithuanianCountyReader, ImportSources
from contactdb.models import CountyStreet, County   
from contactdb.AdressParser import AddressParser
import os

class Command(BaseCommand):
    args = '<number of elelctoral districts (sub-units of counties) to import streets into db>'
    help = 'Imports into database all Lithuanian streets and relates to Lithuanian Counties. \n It is safe to run this command more than once. Before inserting new electoral districts streets, previous streets for same electoral district will be deleted'

    def deleteElectionDistrictIfExists(self, electionDistrict):
        # not sure how to format this line in Python
        # method chaining is nice, but how to format this nicely?
        CountyStreet.objects.filter(electionDistrict = electionDistrict).delete()
        

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


            self.deleteElectionDistrictIfExists(location.ElectionDistrict)
            county = County.objects.get(nr = location.County.nr)


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
            count += 1
            print (u"%d: saved County '%s %d', \nElectoral District '%s' streets (%d). \nTotal streets so far %d" % (count, county.name, county.nr, location.ElectionDistrict, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print "\n\n"
            if (count >= numberToPrint):
                break;
        print "succesfully imported %d counties, total %d streets" % (count, totalNumberOfStreets)