#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cdb_lt_civilparish.models import CivilParishStreet
import logging
from cdb_lt_seniunaitija.models import SeniunaitijaStreet
from cdb_lt_streets.houseNumberUtils import depadHouseNumberWithZeroes
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from cdb_lt_streets.searchMembers import findLT_street_index_id
from cdb_lt_streets.streetUtils import getCityNominative, cityNameIsGenitive, getCityGenitive
from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from pjweb.views import findSeniunaitijaMembers, findCivilParishMembers
from django.db import transaction
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = ''

    def findGeneric(self, streetDataToLooop, functionToCall):
        totalNumberOfStreets = 0

        fromNumber = 0
        toNumber = None
        if len(self.args) >= 1:
            fromNumber, toNumber = ExtractRange(self.args[0])


        if toNumber is not None:
            print "will test streets from %s to %s" % (fromNumber, toNumber)
            allStreets = streetDataToLooop.objects.all()
            allStreets = list(allStreets[fromNumber: toNumber])
        else:
            print "will test all streets"
            allStreets = streetDataToLooop.objects.all()
            allStreets = list(allStreets)


        for streetObject in allStreets:
            totalNumberOfStreets += 1
            municipality = streetObject.municipality
            city = streetObject.city
            house_number = streetObject.numberFrom
            house_number = depadHouseNumberWithZeroes(house_number)
            civilParish =  streetObject.civilParish
            street= streetObject.street
            """municipality = u"Alytaus rajono savivaldybė"
            street = None
            house_number = None
            city = u"Arminų I kaimas"""
            
            additionalKeys = {}
            institutionIdList = findLT_street_index_id(modelToSearchIn=CivilParishStreet, municipality=municipality, civilParish = civilParish, city=city,  street=street, house_number=house_number)
            #members = functionToCall(municipality=municipality, civilParish=civilParish, city=city, street=street, house_number=house_number, **additionalKeys)

            if house_number is None:
                house_number = ""
            if street is None:
                street = ""

            logger.info("row: %s" % (totalNumberOfStreets + fromNumber ))
            total = len(institutionIdList)
            if total == 1:
                continue
            if self.printOnlyStreets == False:
                print "row %s" % (totalNumberOfStreets + fromNumber)
                print "adress: %s %s %s %s" % (street, house_number, city, municipality)
                print "%s institutions found" % total
                print institutionIdList
                print ""
            else:
                print "%s %s %s %s, total %s institutions found %s" % (street, house_number, city, municipality, total, institutionIdList)




        seconds = self.start.ElapsedSeconds()
        if seconds == 0:
            seconds = 1
        rate = str(totalNumberOfStreets / seconds)
        print "checking at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)


    @transaction.commit_on_success
    def handle(self, *args, **options):


        self.printOnlyStreets = True
        self.args = args
        self.start = TimeMeasurer()
        #self.findGeneric(SeniunaitijaStreet, findSeniunaitijaMembers)
        self.findGeneric(CivilParishStreet, findCivilParishMembers)

        print u"total spent time %d seconds" % (self.start.ElapsedSeconds())
        
