#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.imp import LithuanianConstituencyReader, ImportSources, PollingDistrictStreetExpander, SeniunaitijaAddressExpander
from contactdb.models import PollingDistrictStreet, Constituency
from contactdb.AdressParser import AddressParser
from datetime import datetime
from django.db import connection, transaction
from pjutils.timemeasurement import TimeMeasurer
import pjutils.uniconsole
import os
from pjutils.exc import ChainnedException
from test.test_iterlen import len
from contactdb.import_parliamentMembers import SeniunaitijaMembersReader

class Command(BaseCommand):
    args = '<>'
    help = """ """

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
        print "finished pre-fetching. Took %s seconds" % time.ElapsedSeconds()

    def RemoveExistingStreets(self, expandedStreets, street, pollingDistrict):
        nonExisting = []

        # a minor optimization hack, to improve speed when inserting data first time

        # check how many rows we have initially
        if (self.previousDBRowCount is None):
            self.previousDBRowCount = PollingDistrictStreet.objects.count()

        # if we have none rows, then just return list, and do any checks,
        # no need to do that, right
        if (self.previousDBRowCount == 0):
            return expandedStreets

        # will execute looots of selectes against database
        # it will be veerry slow, but works for now
        for expandedStreet in expandedStreets:
            query = PollingDistrictStreet.objects.filter(constituency = pollingDistrict.Constituency)
            query = query.filter(district = pollingDistrict.District)
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
        ImportSources.EsnureExists(ImportSources.LithuanianSeniunaitijaMembers)
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)
        reader = SeniunaitijaMembersReader(allRecords)

        fromPrint = 0
        toPrint = 9999999

        if len(args) > 0:
            if (args[0].find(":") > 0):
                split = args[0].split(':')
                fromPrint = int(split[0])
                toPrint = int(split[1])
            else:
                toPrint = int(args[0])

        streetExpander = SeniunaitijaAddressExpander()


        imported = 0
        totalNumberOfStreets = 0



        start = TimeMeasurer()
        #print "reading polling districts from %s to %s" % (fromPrint, toPrint)
        #allPollingDistricts = self.getPollingDistricts(aggregator, fromPrint, toPrint)

        #self.deletePollingDistrictsIfExists(allPollingDistricts)
        #print "pre-fetching constituencies"
        #self.preFetchAllConstituencies(allPollingDistricts)

        print "starting to import seniunaitija streets"
        count = 0
        for member in reader.ReadMembers():
            if (member.territoryStr == ""):
                continue
            count += 1
            if (fromPrint > count):
                continue
            if (toPrint < count):
                break
            imported += 1
            numberOfStreets = 0
            print "territory for: %s %s" % (member.uniqueKey, member.seniunaitijaStr)
            for street in streetExpander.ExpandStreet(member.territoryStr):
                print "street %s %s %s" % (street.street, street.numberFrom, street.numberTo)
                numberOfStreets += 1

            totalNumberOfStreets += numberOfStreets
            seconds = start.ElapsedSeconds()
            if (seconds == 0):
                rate = "unknown"
            else:
                rate = str(totalNumberOfStreets / seconds)
            #print (u"%d: saved Constituency '%s %d', \nElectoral District '%s' streets (%d). \nTotal streets so far %d" % (count, pollingDistrict.Constituency.name, pollingDistrict.Constituency.nr, pollingDistrict.PollingDistrict, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print (u"%d: saved seniunaitija territory. Number of streets: '%d', \nTotal streets so far %d" % (count, numberOfStreets, totalNumberOfStreets)).encode('utf-8')
            print "inserting at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)
            print "\n\n"


        print "succesfully imported %d seniunaitija territories, total %d streets" % (imported, totalNumberOfStreets)
        print "total spent time %d seconds" % (start.ElapsedSeconds())
