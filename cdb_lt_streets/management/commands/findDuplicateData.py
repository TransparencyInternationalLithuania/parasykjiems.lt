#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models.aggregates import Count
from cdb_lt_civilparish.models import CivilParishStreet, CivilParish, CivilParishMember
import logging
from cdb_lt_mps.models import PollingDistrictStreet, ParliamentMember, Constituency
from cdb_lt_municipality.models import Municipality, MunicipalityMember
from cdb_lt_seniunaitija.models import SeniunaitijaStreet, Seniunaitija, SeniunaitijaMember
from cdb_lt_streets.houseNumberUtils import depadHouseNumberWithZeroes
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from cdb_lt_streets.searchMembers import findLT_street_index_id, findMPs, findMunicipalityMembers
from cdb_lt_streets.streetUtils import getCityNominative, cityNameIsGenitive, getCityGenitive
from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from pjweb.views import findSeniunaitijaMembers, findCivilParishMembers
logger = logging.getLogger(__name__)
from optparse import make_option
from django.db import connection, transaction

class Command(BaseCommand):
    args = '<>'
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('-d', '--member',
            dest='member',
            metavar="member",
            default = "civilParish",
            help='Choose one of 4 members to check: civilParish, MP, seniunaitija, municipality'),
        )


    def getDistinctStreetCount(self, streetModel):
        dbTable = streetModel.objects.model._meta.db_table
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM (SELECT DISTINCT municipality, city, street FROM %s)  as t" % (dbTable))
        row = cursor.fetchone()
        return row[0]

    def findGeneric(self, streetModel = None, institutions = None, memberModel = None):
        totalNumberOfStreets = 0

        fromNumber = 0
        toNumber = None
        if len(self.args) >= 1:
            fromNumber, toNumber = ExtractRange(self.args[0])

        count = self.getDistinctStreetCount(streetModel=streetModel)
        print "count %s " % count

        if toNumber is not None:
            print "will test streets from %s to %s" % (fromNumber, toNumber)
            allStreets = streetModel.objects.all()
            allStreets.query.group_by = ['municipality', 'city', 'street']
            allStreets = allStreets[fromNumber:toNumber]
        else:
            print "will test all streets"
            allStreets = streetModel.objects.all()
        allStreets = list(allStreets)

        streetsWithMultipleInstitutions = {}

        allStreetCount = len(allStreets)
        #print "total %s streets to test" % allStreetCount


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
            institutionIdList = findLT_street_index_id(modelToSearchIn=streetModel, municipality=municipality, civilParish = civilParish, city=city,  street=street, house_number=house_number)
            #members = functionToCall(municipality=municipality, civilParish=civilParish, city=city, street=street, house_number=house_number, **additionalKeys)

            if house_number is None:
                house_number = ""
            if street is None:
                street = ""

            if totalNumberOfStreets % 100 == 0:
                logger.info("row: %s,  %s%%" % (totalNumberOfStreets + fromNumber, totalNumberOfStreets / float(allStreetCount) * 100 ))

            total = len(institutionIdList)
            if total == 1:
                continue
            hash = "%s %s %s" % (municipality, city, street)
            if streetsWithMultipleInstitutions.has_key(hash) == False:
                lst = []
            else:
                lst = streetsWithMultipleInstitutions[hash]
            # attach street object, and list of institution objects
            inst = [institutions[id] for id in institutionIdList]
            lst.append((streetObject, inst))
            streetsWithMultipleInstitutions[hash] = lst
                
            """if self.printOnlyStreets == False:
                print "row %s" % (totalNumberOfStreets + fromNumber)
                print "adress: %s %s %s %s" % (street, house_number, city, municipality)
                print "%s institutions found" % total
                print institutionIdList
                print ""
            else:
                print "%s %s %s %s, total %s institutions found %s" % (street, house_number, city, municipality, total, institutionIdList)
            """

        seconds = self.start.ElapsedSeconds()
        if seconds == 0:
            seconds = 1
        rate = str(totalNumberOfStreets / seconds)
        print "checked at %s rows per second (total sec: %d, rows: %d)" % (rate, seconds, totalNumberOfStreets)

        print "\n\n"
        for val in streetsWithMultipleInstitutions.itervalues():
            streetObject = val[0][0]
            print "%s %s %s %s" % (streetObject.street, streetObject.civilParish, streetObject.city, streetObject.municipality)
            for s, institutions in val:
                institutionNames = [inst.name for inst in institutions]
                if s.numberFrom == u"":
                    street = u"Visa gatvė"
                else:
                    street = depadHouseNumberWithZeroes(s.numberFrom)
                print u"Gatvės numeris: %s.    Priklauso šioms seniūnijoms: %s" % (street, u", ".join(institutionNames))
            print "\n"

        print "percent of incorrect data %s%%" % (len(streetsWithMultipleInstitutions) / float(count) * 100)




    @transaction.commit_on_success
    def handle(self, *args, **options):

        print u"memberType set to %s" % options['member']
        memberType = options['member']

        allMemberTypes = {"civilParish": (CivilParishStreet, CivilParish, CivilParishMember),
                          "seniunaitija": (SeniunaitijaStreet, Seniunaitija, SeniunaitijaMember),
                          "municipality": (None, Municipality, MunicipalityMember),
                          "MP": (PollingDistrictStreet, Constituency, ParliamentMember)
        }

        if not allMemberTypes.has_key(memberType):
            print "Unrecognized type, %s. Possible values %s " % (memberType, list(allMemberTypes.iterkeys()))
            return

        streetModel, institutionModel, memberModel = allMemberTypes[memberType]


        

        self.printOnlyStreets = True
        self.args = args
        self.start = TimeMeasurer()

        print "member function %s" % memberModel
        institutions = dict((p.id, p) for p in institutionModel.objects.all())
        self.findGeneric(streetModel=streetModel, memberModel= memberModel, institutions = institutions)

        print u"total spent time %d seconds" % (self.start.ElapsedSeconds())
        
