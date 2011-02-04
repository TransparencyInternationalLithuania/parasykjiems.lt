#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cdb_lt_seniunaitija.models import SeniunaitijaStreet
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from cdb_lt_streets.streetUtils import getCityNominative
from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from pjweb.views import findSeniunaitijaMembers
from django.db import transaction

class Command(BaseCommand):
    args = '<>'
    help = ''

    @transaction.commit_on_success
    def handle(self, *args, **options):

        totalNumberOfStreets = 0

        fromNumber = 0
        toNumber = None
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])


        if toNumber is not None:
            print "will test streets from %s to %s" % (fromNumber, toNumber)
            allStreets = SeniunaitijaStreet.objects.all()
            allStreets = list(allStreets[fromNumber: toNumber])
        else:
            print "will test all streets"
            allStreets = SeniunaitijaStreet.objects.all()
            allStreets = list(allStreets)

        start = TimeMeasurer()
        for streetObject in allStreets:
            print "row %s" % (totalNumberOfStreets + fromNumber)
            totalNumberOfStreets += 1
            municipality = streetObject.municipality
            city = streetObject.city
            house_number = streetObject.numberFrom
            city_genitive = city
            street = streetObject.street
            city = getCityNominative(municipality=municipality, city_genitive=city_genitive, street= street)


            """municipality = u"Šilalės rajono"
            city_genitive = u"Kalniškių kaimas"
            street = None
            house_number = None
            city = None"""

            additionalKeys = {"city_genitive" : city_genitive}
            members = findSeniunaitijaMembers(municipality, city, street, house_number, **additionalKeys)

            if house_number is None:
                house_number = ""
            if street is None:
                street = ""

            total = len(members)
            if total == 1:
                continue
            print "adress: %s %s %s %s" % (street, house_number, city_genitive, municipality)
            print "%s member" % total

            for m in members:
                print "%s %s" % (m.name, m.surname)

            print ""

        seconds = start.ElapsedSeconds()
        rate = str(totalNumberOfStreets / seconds)
        print "checking at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)

        print u"total spent time %d seconds" % (start.ElapsedSeconds())
        
