#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys

from django.core.management.base import BaseCommand
from django.core import management
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from cdb_lt_streets.searchInIndex import deduceAddress, searchInIndex
from cdb_lt_streets.searchMembers import findMPs, findMunicipalityMembers, findCivilParishMembers, findSeniunaitijaMembers
import os
from pjutils.timemeasurement import TimeMeasurer
from settings import GlobalSettings

class Command(BaseCommand):
    args = '<>'
    help = """Searches for members against hand-written list of addresses and checks whether exactly 1 representative is returned"""

    def testAddresses(self, addresses):
        functions = [findMPs,
                     findMunicipalityMembers,
                     findCivilParishMembers,
                     findSeniunaitijaMembers]

        missingDataByStreet = {}

        count = 0
        total = len(addresses)
        for address in addresses:

            address = address.strip()
            if address == u"":
                continue
            if address.find(u"--") >=0:
                continue

            count += 1

            if missingDataByStreet.has_key(address):
                continue

            if count % 100 == 0:
                sec = self.start.ElapsedSeconds()
                print "tested %s from %s, percentage tested: %s.  Elapsed seconds %s, %s seconds per row" % (count, total, count / float(total), sec, sec / float(count))


            addressContext = deduceAddress(address)
            found_entries = searchInIndex(municipality= addressContext.municipality, city= addressContext.city, street= addressContext.street)

            missingDataByStreet.setdefault(address, [address, len(found_entries)])
            if len(found_entries) != 1:
                continue

            f = found_entries[0]
            civilParish = f.civilparish
            municipality = f.municipality
            city = f.city_genitive
            street = f.street
            house_number = addressContext.number

            additionalKeys = {'municipality':municipality,
                              'civilParish':civilParish,
                              'city':city,
                              'street':street,
                              'house_number':house_number}

            for function in functions:
                members = function(**additionalKeys)
                missingDataByStreet[address].append(len(members))
                
        """print u"total spent time %d seconds" % (self.start.ElapsedSeconds())
        if count == 0:
            print "Total rows %s, %s seconds per row" % (count, 0)
        else:
            print "Total rows %s, %s seconds per row" % (count, self.start.ElapsedSeconds() / float(count))"""
        return missingDataByStreet
        


    def readAddresses(self, addressFile):
        curDir = os.getcwd()

        file = os.path.join(curDir, addressFile)
        f = open(file, mode="r")
        addresses = f.readlines()
        addresses = [unicode(val.strip(), 'utf-8') for val in addresses]
        return addresses

    def printPercentages(self, missingDataByStreet, allAddresses):
        totalStreets = len(allAddresses)

        incorrectData = [0, 0, 0, 0, 0, 0]

        for address, values in missingDataByStreet.iteritems():
            for i in range(1, len(values)):
                count = values[i]
                if count != 1:
                    incorrectData[i] += 1

        print u"Iš viso gatvių: %s" % totalStreets
        labels = [u"Gatvių", u"Seimo narių", u"Merų", u"Seniūnų", u"Seniūnaičių"]
        for i in range(0, len(labels)):
            print "%s %s: %s%%" % (labels[i], incorrectData[i + 1], incorrectData[i + 1] / float(totalStreets) * 100)
        print "\n\n"


        

    def handle(self, *args, **options):
        """ Not very usefull command, until we know what result exactly we want. Now will print lots of information when running.
        Will search for every address in addresses list and check if exactly one member is found"""

        self.start = TimeMeasurer()

        fromNumber = 0
        toNumber = None
        if len(args) >= 2:
            fromNumber, toNumber = ExtractRange(args[1])

        if len(args) > 0:
            addresses = self.readAddresses(args[0])
        else:
            print "Please specify file with addresses"
            return

        addresses = addresses[fromNumber: toNumber]
        missingDataByStreet = self.testAddresses(addresses)

        print "\n\n"

        self.printPercentages(missingDataByStreet, addresses)


        # print as csv style
        writer = csv.writer(sys.stdout)
        header = [u'Adresas', u'Surasta adresų', u'Seimo narys', u'Meras', u'Seniūnas', u'Seniūnaitis']
        header = [v.encode('utf-8') for v in header]
        writer.writerow(header)
        for address, values in missingDataByStreet.iteritems():
            values = ["%s" % v for v in values]
            values = [v.encode('utf-8') for v in values ]
            writer.writerow(values)
