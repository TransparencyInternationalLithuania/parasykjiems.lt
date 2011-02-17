#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core import management
from cdb_lt_streets.searchInIndex import deduceAddress, searchInIndex
from cdb_lt_streets.searchMembers import findMPs, findMunicipalityMembers, findCivilParishMembers, findSeniunaitijaMembers


class Command(BaseCommand):
    args = '<>'
    help = """Searches for members against hand-written list of addresses and checks whether exactly 1 representative is returned"""

    def handle(self, *args, **options):
        """ Not very usefull command, until we know what result exactly we want. Now will print lots of information when running.
        Will search for every address in addresses list and check if exactly one member is found"""


        addresses = [u"Palemono 74",
                    u"žygio g., Vilnius",
                    u"sodų g. vilnius",
                    u"šaulių 23a, klaipėda"]

        functions = {"MP": findMPs,
                     "Mayor": findMunicipalityMembers,
                     "CivilParish": findCivilParishMembers,
                     "Seniunaitija": findSeniunaitijaMembers}

        missingData = {"MP": [],
                     "Mayor": [],
                     "CivilParish": [],
                     "Seniunaitija": []}

        for address in addresses:
            addressContext = deduceAddress(address)
            found_entries = searchInIndex(municipality= addressContext.municipality, city= addressContext.city, street= addressContext.street)

            if len(found_entries) != 1:
                print "Found more than one entry for address %s " % address
                print found_entries

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


        print "\n\n"
        for type, queue in missingData.iteritems():
            print "\n"
            print "printing missing data for %s" % type

            for item in queue:
                street, members = item
                print "%s \t: %s members" % (street.rjust(25, ' '), len(members))







