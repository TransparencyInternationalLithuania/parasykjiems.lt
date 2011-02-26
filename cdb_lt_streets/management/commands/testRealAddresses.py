#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core import management
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from cdb_lt_streets.searchInIndex import deduceAddress, searchInIndex
from cdb_lt_streets.searchMembers import findMPs, findMunicipalityMembers, findCivilParishMembers, findSeniunaitijaMembers
import os
from pjutils.timemeasurement import TimeMeasurer

class Command(BaseCommand):
    args = '<>'
    help = """Searches for members against hand-written list of addresses and checks whether exactly 1 representative is returned"""


    def getDefaultAddresses(self):
        return [u"Palemono 74",
                    u"žygio g., Vilnius",
                    u"sodų g. vilnius",
                    u"šaulių 23a, klaipėda",
                    u"J. Žemgulio gatvė 10 Kauno miestas Kauno miesto savivaldybė"]


    def handle(self, *args, **options):
        """ Not very usefull command, until we know what result exactly we want. Now will print lots of information when running.
        Will search for every address in addresses list and check if exactly one member is found"""

        exactQueries = []
        addresses = []
        self.start = TimeMeasurer()

        fromNumber = 0
        toNumber = None
        if len(args) >= 2:
            fromNumber, toNumber = ExtractRange(args[1])

        if len(args) > 0:
            file = args[0]
            curDir = os.getcwd()

            file = os.path.join(curDir, file)
            f = open(file, mode="r")
            addresses = f.readlines()
            addresses = [unicode(val.strip(), 'utf-8') for val in addresses]
        else:
            addresses = self.getDefaultAddresses()

            exactQueries = [{'municipality':u"Šilutės rajono savivaldybė",
                              'civilParish':u"Šilutės seniūnija",
                              'city':u"Kalininkų kaimas",
                              'street':u"",
                              'house_number':u""}
            ]


        functions = {"MP": findMPs,
                     "Mayor": findMunicipalityMembers,
                     "CivilParish": findCivilParishMembers,
                     "Seniunaitija": findSeniunaitijaMembers}

        missingData = {"MP": [],
                     "Mayor": [],
                     "CivilParish": [],
                     "Seniunaitija": []}

        addresses = addresses[fromNumber: toNumber]
        count = 0
        total = len(addresses)
        for address in addresses:

            address = address.strip()
            if address == u"":
                continue
            if address.find(u"--") >=0:
                continue

            count += 1
            print "%s" % address

            if count % 100 == 0:
                sec = self.start.ElapsedSeconds()
                print "tested %s from %s, percentage tested: %s.  Elapsed seconds %s, %s seconds per row" % (count, total, count / float(total), sec, sec / float(count))


            addressContext = deduceAddress(address)
            found_entries = searchInIndex(municipality= addressContext.municipality, city= addressContext.city, street= addressContext.street)

            if len(found_entries) != 1:
                print "Found more than one entry for address %s " % address
                print found_entries
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

            for key, function in functions.iteritems():
                members = function(**additionalKeys)
                if len(members) != 1:
                    queue = missingData[key]
                    queue.append([address, members])

        for keys in exactQueries:
            for key, function in functions.iteritems():
                members = function(**keys)
                if len(members) != 1:
                    queue = missingData[key]
                    addr = u"%s %s %s" % (keys['municipality'], keys['civilParish'], keys['city'])
                    queue.append([addr, members])





        print "\n\n"
        # print streets and percentages
        for type, queue in missingData.iteritems():
            print "\n"
            print "missing data for %s" % type

            for item in queue:
                street, members = item
                print "%s \t: %s members" % (street.rjust(25, ' '), len(members))
            print "total rows: %s " % count
            print "total incorrect results: %s" % len(queue)
            if len(queue) == 0:
                print "percentage %s%%" % (0.00)
            else:
                print "percentage %s%%" % (float(len(queue))/ count * 100)


        # just print percentages
        print "\n\n\n"
        for type, queue in missingData.iteritems():
            print "\n"
            print "missing data for %s" % type
            print "total rows: %s " % count
            print "total incorrect results: %s" % len(queue)
            if len(queue) == 0:
                print "percentage %s%%" % (0.00)
            else:
                print "percentage %s%%" % (float(len(queue))/ count * 100)

        print u"total spent time %d seconds" % (self.start.ElapsedSeconds())






