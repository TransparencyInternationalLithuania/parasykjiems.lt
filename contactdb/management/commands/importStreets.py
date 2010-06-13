#!/usr/bin/env python
# -*- coding: utf8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.imp import LithuanianCountyReader, ImportSources
from contactdb.models import CountyStreet, County   
from contactdb.AdressParser import AddressParser
from datetime import datetime
from django.db import connection, transaction
from contactdb.timemeasurement import TimeMeasurer

import os

class Command(BaseCommand):
    args = '<number of elelctoral districts (sub-units of counties) to import streets into db>'
    help = """Imports into database all Lithuanian streets and relates to Lithuanian Counties
It is safe to run this command more than once. Before inserting new electoral districts streets, previous streets for same electoral district will be deleted
Examples:
importStreets 5 - will import streets for first 5 Election Districts. If run repeatedly, result will be the same, except that manually entered data will be deleted
importStreets 5:8 - will import streets for counties from 5 to 8 county inclusive  """

    def deleteElectionDistrictIfExists(self, electionDistrict):
        CountyStreet.objects.filter(electionDistrict = electionDistrict).delete()

    def deleteElectionDistrictIfExistsInBatch(self, names):
        """ pass a collection of polling district names in names. They will
        get deleted with delete from table in () statemenet """
        dbTable = CountyStreet.objects.model._meta.db_table
        # why 5?  Because it is ElectionDistrict field. And also since i do not know how to get it automatically
        columnName = CountyStreet.objects.model._meta.fields[5].column
        sql = "delete from %s where %s in (%s)" % (dbTable, columnName, names)
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()

    @transaction.commit_on_success
    def deleteElectionDistrictsIfExists(self, pollingDistricts):
        time = TimeMeasurer()
        print "deleting previous data"

        batch = 20



        districtNames = []
        currentBatch = 0
        for pol in pollingDistricts.itervalues():
            if (currentBatch >= batch):
                currentBatch = 0
                names = "', '".join(districtNames)
                self.deleteElectionDistrictIfExistsInBatch(names)
                districtNames = []

            districtNames.append("'%s'" % pol.ElectionDistrict)
            currentBatch += 1
            #self.deleteElectionDistrictIfExists(pol.ElectionDistrict)

        names = "', '".join(districtNames)
        self.deleteElectionDistrictIfExistsInBatch(names)
        print "finished deleting. Took %s seconds" % time.ElapsedSeconds()


    def getPollingDistricts(self, aggregator, fromPrint, toPrint):
        count = 0

        pollingDistricts = {}

        for pollingDistrict in aggregator.getLocations():
            if (count + 1 > toPrint):
                break
            count += 1
            if (count + 1 <= fromPrint):
                continue
            pollingDistricts[count] = pollingDistrict
        return pollingDistricts



    def preFetchAllConstituencies(self, pollingDistricts):
        time = TimeMeasurer()
        # fetch all counties in pseudo batch,
        constituencies = {}

        for pol in pollingDistricts.itervalues():
            if (constituencies.has_key(pol.County.nr) == False):
                constituencies[pol.County.nr] = County.objects.get(nr = pol.County.nr)

            county = constituencies[pol.County.nr]
            # re-assign old constituency to new constituency fetched from database
            pol.County = county
        print "finished pre-fetching. Took %s seconds" % time.ElapsedSeconds()


    @transaction.commit_on_success    
    def handle(self, *args, **options):
        allRecords = os.getcwd() + ImportSources.LithuanianCounties
        file = open(allRecords, "r")
        aggregator = LithuanianCountyReader(file)


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


        imported = 0
        totalNumberOfStreets = 0



        start = datetime.now()
        print "reading all polling districts"
        allPollingDistricts = self.getPollingDistricts(aggregator, fromPrint, toPrint)

        self.deleteElectionDistrictsIfExists(allPollingDistricts)
        print "pre-fetching constituencies"
        self.preFetchAllConstituencies(allPollingDistricts)

        print "starting to import streets"
        for count, pollingDistrict in allPollingDistricts.iteritems():
            imported += 1
            numberOfStreets = 0
            for street in streetParser.GetAddresses(pollingDistrict.Addresses):
                countyStreet = CountyStreet()
                countyStreet.county = pollingDistrict.County
                countyStreet.district = pollingDistrict.District
                countyStreet.city = street.cityName
                countyStreet.street = street.streetName
                countyStreet.electionDistrict = pollingDistrict.ElectionDistrict
                countyStreet.save()
                numberOfStreets += 1

            totalNumberOfStreets += numberOfStreets
            seconds = (datetime.now() - start).seconds
            if (seconds == 0):
                rate = "unknown"
            else:
                rate = str(totalNumberOfStreets / seconds)
            print (u"%d: saved County '%s %d', \nElectoral District '%s' streets (%d). \nTotal streets so far %d" % (count, pollingDistrict.County.name, pollingDistrict.County.nr, pollingDistrict.ElectionDistrict, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print "inserting at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)
            print "\n\n"


        print "succesfully imported %d counties, total %d streets" % (imported, totalNumberOfStreets)
        print "total spent time %d seconds" % (datetime.now() - start).seconds