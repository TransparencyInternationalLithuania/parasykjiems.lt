#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.imp import ImportSources
from datetime import datetime
from django.db import connection, transaction
from pjutils.timemeasurement import TimeMeasurer
import pjutils.uniconsole
import os
from pjutils.exc import ChainnedException
from cdb_lt_mps.parseConstituencies import LithuanianConstituencyReader, PollingDistrictStreetExpander, AddressParser
from cdb_lt_mps.models import Constituency, PollingDistrictStreet

class ImportStreetsConstituencyDoesNotExist(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<number of elelctoral districts (sub-units of counties) to import streets into db>'
    help = """Imports into database all Lithuanian streets and relates to Lithuanian Counties
It is safe to run this command more than once. Does not delete any data, only inserts additional.
Does not update existing data either, as there is no unique-key by which to identify.

Examples:
importStreets 5 - will import streets for first 5 Election Districts. If run repeatedly, result will be the same, except that manually entered data will be deleted
importStreets 5:8 - will import streets for counties from 5 to 8 constituencies inclusive  """

    previousDBRowCount = None

    def getPollingDistricts(self, aggregator, fromPrint, toPrint):
        count = 0

        pollingDistricts = []

        for pollingDistrict in aggregator.getLocations():
            if (count + 1 > toPrint):
                break
            count += 1
            if (count + 1 <= fromPrint):
                continue
            pollingDistricts.append(pollingDistrict)
        return pollingDistricts



    def preFetchAllConstituencies(self, pollingDistricts):
        time = TimeMeasurer()
        # fetch all counties in pseudo batch,
        constituencies = {}

        for pol in pollingDistricts:
            if (constituencies.has_key(pol.Constituency.nr) == False):
                try:
                    constituencies[pol.Constituency.nr] = Constituency.objects.get(nr = pol.Constituency.nr)
                except Constituency.DoesNotExist as e:
                    raise ImportStreetsConstituencyDoesNotExist("constituency '%s' was not found in DB. Maybe you forgot to import them : manage.py importConstituencies?  Or else it might not exist in source data, in which case you will have to resolve manually this issue", e)


            constituency = constituencies[pol.Constituency.nr]
            # re-assign old constituency to new constituency fetched from database
            pol.Constituency = constituency
        print u"finished pre-fetching. Took %s seconds" % time.ElapsedSeconds()

    def RemoveExistingStreets(self, expandedStreets, street, pollingDistrict):
        """ filters a list of streets and returns a list only with those streets,
        which do not exist already in database. Does not delete anything in database"""
        nonExisting = []

        # a minor optimization hack, to improve speed when inserting data first time

        # check how many rows we have initially
        if (self.previousDBRowCount is None):
            self.previousDBRowCount = PollingDistrictStreet.objects.count()

        # if we have none rows, then just return list, and do any checks,
        # no need to do that, right
        if (self.previousDBRowCount == 0):
            return expandedStreets

        # will execute lots of selects against database
        # it will be very slow, but works for now
        for expandedStreet in expandedStreets:
            query = PollingDistrictStreet.objects.filter(constituency = pollingDistrict.Constituency)
            query = query.filter(city = street.cityName)
            query = query.filter(street = expandedStreet.street)
            query = query.filter(pollingDistrict = pollingDistrict.PollingDistrict)
            query = query.filter(numberFrom = expandedStreet.numberFrom)
            query = query.filter(numberTo = expandedStreet.numberTo)
            #print query.query
            results = list(query)

            if (len(results) == 0):
                nonExisting.append(expandedStreet)

        return nonExisting


    @transaction.commit_on_success    
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianConstituencies)
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianConstituencies)
        file = open(allRecords, "r")
        aggregator = LithuanianConstituencyReader(file)


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
        streetExpander = PollingDistrictStreetExpander()


        imported = 0
        totalNumberOfStreets = 0



        start = datetime.now()
        print "reading polling districts from %s to %s" % (fromPrint, toPrint)
        allPollingDistricts = self.getPollingDistricts(aggregator, fromPrint, toPrint)

        #self.deletePollingDistrictsIfExists(allPollingDistricts)
        print u"pre-fetching constituencies"
        self.preFetchAllConstituencies(allPollingDistricts)

        print u"starting to import streets"
        count = 0
        for pollingDistrict in allPollingDistricts:
            count += 1
            imported += 1
            numberOfStreets = 0
            for street in streetParser.GetAddresses(pollingDistrict.Addresses):
                expandedStreets = list(streetExpander.ExpandStreet(street.streetName))
                expandedStreets = self.RemoveExistingStreets(expandedStreets, street, pollingDistrict)
                for expandedStreet in expandedStreets:            
                    pollingDistrictStreet = PollingDistrictStreet()
                    pollingDistrictStreet.constituency = pollingDistrict.Constituency
                    pollingDistrictStreet.municipality = pollingDistrict.District
                    pollingDistrictStreet.city = street.cityName
                    expandedStreetStr = expandedStreet.street
                    pollingDistrictStreet.street = expandedStreetStr
                    pollingDistrictStreet.numberFrom =  expandedStreet.numberFrom
                    pollingDistrictStreet.numberTo = expandedStreet.numberTo
                    if (expandedStreet.numberFrom is not None):
                        pollingDistrictStreet.numberOdd = expandedStreet.numberFrom % 2
                    pollingDistrictStreet.pollingDistrict = pollingDistrict.PollingDistrict
                    pollingDistrictStreet.save()
                    numberOfStreets += 1

            totalNumberOfStreets += numberOfStreets
            seconds = (datetime.now() - start).seconds
            if (seconds == 0):
                rate = "unknown"
            else:
                rate = str(totalNumberOfStreets / seconds)
            #print (u"%d: saved Constituency '%s %d', \nElectoral District '%s' streets (%d). \nTotal streets so far %d" % (count, pollingDistrict.Constituency.name, pollingDistrict.Constituency.nr, pollingDistrict.PollingDistrict, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print (u"%d: saved Constituency. Number of streets: '%d', \nTotal streets so far %d" % (count, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print u"inserting at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)
            print "\n\n"


        print u"succesfully imported %d counties, total %d streets" % (imported, totalNumberOfStreets)
        print u"total spent time %d seconds" % (datetime.now() - start).seconds
