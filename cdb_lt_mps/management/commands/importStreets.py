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
from cdb_lt_streets.houseNumberUtils import isHouseNumberOdd

class ImportStreetsConstituencyDoesNotExist(ChainnedException):
    pass


municipalities = {
        u"Akmenės rajonas":u"Akmenės rajono savivaldybė",
        u"Alytaus miestas":u"Alytaus miesto savivaldybė",
        u"Alytaus rajonas":u"Alytaus rajono savivaldybė",
        u"Anykščių rajonas":u"Anykščių rajono savivaldybė",
        u"BirštonAS":u"Birštono savivaldybė",
        u"Biržų rajonas":u"Biržų rajono savivaldybė",
        u"Druskininkų miestas":u"Druskininkų savivaldybė",
        u"Elektrėnai":u"Elektrėnų savivaldybė",
        u"Ignalinos rajonas":u"Ignalinos rajono savivaldybė",
        u"Jonavos rajonas":u"Jonavos rajono savivaldybė",
        u"Joniškio rajonas":u"Joniškio rajono savivaldybė",
        u"Jurbarko rajonas":u"Jurbarko rajono savivaldybė",
        u"Kaišiadorių rajonas":u"Kaišiadorių rajono savivaldybė",
        u"Kalvarija":u"Kalvarijos savivaldybė",
        u"Kauno miestas":u"Kauno miesto savivaldybė",
        u"Kauno rajonas":u"Kauno rajono savivaldybė",
        u"Kazlų RūdA":u"Kazlų Rūdos savivaldybė",
        u"Kelmės rajonas":u"Kelmės rajono savivaldybė",
        u"Klaipėdos miestas":u"Klaipėdos miesto savivaldybė",
        u"Klaipėdos rajonas":u"Klaipėdos rajono savivaldybė",
        u"Kretingos rajonas":u"Kretingos rajono savivaldybė",
        u"Kupiškio rajonas":u"Kupiškio rajono savivaldybė",
        u"Kėdainių rajonas":u"Kėdainių rajono savivaldybė",
        u"Lazdijų rajonas":u"Lazdijų rajono savivaldybė",
        u"Marijampolės miestas":u"Marijampolės savivaldybė",
        u"Mažeikių rajonas":u"Mažeikių rajono savivaldybė",
        u"Molėtų rajonas":u"Molėtų rajono savivaldybė",
        u"NeringA":u"Neringos savivaldybė",
        u"PagėgIAI":u"Pagėgių savivaldybė",
        u"Pakruojo rajonas":u"Pakruojo rajono savivaldybė",
        u"Palangos miestas":u"Palangos miesto savivaldybė",
        u"Panevėžio miestas":u"Panevėžio miesto savivaldybė",
        u"Panevėžio rajonas":u"Panevėžio rajono savivaldybė",
        u"Pasvalio rajonas":u"Pasvalio rajono savivaldybė",
        u"Plungės rajonas":u"Plungės rajono savivaldybė",
        u"Prienų rajonas":u"Prienų rajono savivaldybė",
        u"Radviliškio rajonas":u"Radviliškio rajono savivaldybė",
        u"Raseinių rajonas":u"Raseinių rajono savivaldybė",
        u"RietavAS":u"Rietavo savivaldybė",
        u"Rokiškio rajonas":u"Rokiškio rajono savivaldybė",
        u"Skuodo rajonas":u"Skuodo rajono savivaldybė",
        u"Tauragės rajonas":u"Tauragės rajono savivaldybė",
        u"Telšių rajonas":u"Telšių rajono savivaldybė",
        u"Trakų rajonas":u"Trakų rajono savivaldybė",
        u"Ukmergės rajonas":u"Ukmergės rajono savivaldybė",
        u"Utenos rajonas":u"Utenos rajono savivaldybė",
        u"Varėnos rajonas":u"Varėnos rajono savivaldybė",
        u"Vilkaviškio rajonas":u"Vilkaviškio rajono savivaldybė",
        u"Vilniaus miestas":u"Vilniaus miesto savivaldybė",
        u"Vilniaus rajonas":u"Vilniaus rajono savivaldybė",
        u"VisaginAS":u"Visagino savivaldybė",
        u"Zarasų rajonas":u"Zarasų rajono savivaldybė",
        u"Šakių rajonas":u"Šakių rajono savivaldybė",
        u"Šalčininkų rajonas":u"Šalčininkų rajono savivaldybė",
        u"Šiaulių miestas":u"Šiaulių miesto savivaldybė",
        u"Šiaulių rajonas":u"Šiaulių rajono savivaldybė",
        u"Šilalės rajonas":u"Šilalės rajono savivaldybė",
        u"Šilutės rajonas":u"Šilutės rajono savivaldybė",
        u"Širvintų rajonas":u"Širvintų rajono savivaldybė",
        u"Švenčionių rajonas":u"Švenčionių rajono savivaldybė"}

def changeMunicipalityToCorrectForm(municipality):
    if not MunicipalityCases.has_key(municipality):
        raise ImportStreetsConstituencyDoesNotExist(message="municipality '%s' was not found in standard municipality form list" % municipality)
    return municipalities[municipality]

def changeToGenitiveCityName(city):
    cities = {
        u"Akmenė":u"Akmenės miestas",
        u"Alytus":u"Alytaus miestas",
        u"Anykščiai":u"Anykščių miestas",
        u"Ariogala":u"Ariogalos miestas",
        u"Baltoji Vokė":u"Baltosios Vokės miestas",
        u"Birštonas":u"Birštono miestas",
        u"Biržai":u"Biržų miestas",
        u"Daugai":u"Daugų miestas",
        u"Didieji Gulbinai":u"Didžiųjų Gulbinų kaimas",
        u"Druskininkai":u"Druskininkų miestas",
        u"Dusetos":u"Dusetų miestas",
        u"Dūkštas":u"Dūkšto miestas",
        u"Eišiškės":u"Eišiškių miestas",
        u"Elektrėnai":u"Elektrėnų miestas",
        u"Ežerėlis":u"Ežerėlio miestas",
        u"Galgiai":u"Galgių kaimas",
        u"Gargždai":u"Gargždų miestas",
        u"Garliava":u"Garliavos miestas",
        u"Gelgaudiškis":u"Gelgaudiškio miestas",
        u"Grigiškės":u"Grigiškių miestas",
        u"Ignalina":u"Ignalinos miestas",
        u"Jieznas":u"Jiezno miestas",
        u"Jonava":u"Jonavos miestas",
        u"Joniškis":u"Joniškio miestas",
        u"Joniškėlis":u"Joniškėlio miestas",
        u"Jurbarkas":u"Jurbarko miestas",
        u"Kaišiadorys":u"Kaišiadorių miestas",
        u"Kalvarija":u"Kalvarijų miestas",
        u"Kaunas":u"Kauno miestas",
        u"Kavarskas":u"Kavarsko miestas",
        u"Kazlų Rūda":u"Kazlų Rūdos miestas",
        u"Kačerginė":u"Kačerginės miestelis",
        u"Kelmė":u"Kelmės miestas",
        u"Klaipėda":u"Klaipėdaos miestas",
        u"Kretinga":u"Kretingo smiestas",
        u"Kudirkos Naumiestis":u"Kudirkos Naumiesčio miestas",
        u"Kupiškis":u"Kupiškio miestas",
        u"Kuršėnai":u"Kuršėnų miestas",
        u"Kybartai":u"Kybartų miestas",
        u"Kėdainiai":u"Kėdainių miestas",
        u"Lazdijai":u"Lazdijų miestas",
        u"Lentvaris":u"Lentvario miestas",
        u"Linkuva":u"Linkuvos miestas",
        u"Marijampolė":u"Marijampolės miestas",
        u"Mažeikiai":u"Mažeikių miestas",
        u"Molėtai":u"Molėtų miestas",
        u"Naujoji Akmenė":u"Naujosios Akmenės miestas",
        u"Nemenčinė":u"Nemenčinės miestas",
        u"Neringa":u"Neringos miestas",
        u"Obeliai":u"Obelių miestas",
        u"Pabradė":u"Pabradės miestas",
        u"Pagėgiai":u"Pagėgių miestas",
        u"Pakruojis":u"Pakruojo miestas",
        u"Palanga":u"Palangos miestas",
        u"Pandėlys":u"Pandėlio miestas",
        u"Panemunė":u"Panemunės miestas",
        u"Panevėžys":u"Panevėžio miestas",
        u"Pasvalys":u"Pasvalio miestas",
        u"Plungė":u"Plungės miestas",
        u"Priekulė":u"Priekulės miestas",
        u"Prienai":u"Prienų miestas",
        u"Radviliškis":u"Radviliškio miestas",
        u"Raseiniai":u"Raseinių miestas",
        u"Rietavas":u"Rietavo miestas",
        u"Rokiškis":u"Rokiškio miestas",
        u"Rusnė":u"Rusnės miestas",
        u"Rūdiškės":u"Rūdiškių miestas",
        u"Simnas":u"Simno miestas",
        u"Skaudvilė":u"Skaudvilės miestas",
        u"Skuodas":u"Skuodo miestas",
        u"Smalininkai":u"Smalininkų miestas",
        u"Tauragė":u"Tauragės miestas",
        u"Telšiai":u"Telšių miestas",
        u"Trakai":u"Trakų miestas",
        u"Troškūnai":u"Troškūnų miestas",
        u"Tyruliai":u"Tyrulių miestas",
        u"Tytuvėnai":u"Tytuvėnų miestas",
        u"Ukmergė":u"Ukmergės miestas",
        u"Utena":u"Utenos miestas",
        u"Užventis":u"Užvenčio miestas",
        u"Vabalninkas":u"Vabalninko miestas",
        u"Varniai":u"Varnių miestas",
        u"Varėna":u"Varėnos miestas",
        u"Veisiejai":u"Veisiejų miestas",
        u"Venta":u"Ventos miestas",
        u"Viekšniai":u"Viekšnių miestas",
        u"Vievis":u"Vievio miestas",
        u"Vilkaviškis":u"Vilkaviškio miestas",
        u"Vilkija":u"Vilkijos miestas",
        u"Vilnius":u"Vilniaus miestas",
        u"Virbalis":u"Virbalio miestas",
        u"Visaginas":u"Visagino miestas",
        u"Zarasai":u"Zarasų miestas",
        u"Šakiai":u"Šakių miestas",
        u"Šalčininkai":u"Šalčininkų miestas",
        u"Šeduva":u"Šeduvos miestas",
        u"Šiauliai":u"Šiaulių miestas",
        u"Šilalė":u"Šilalės miestas",
        u"Šilutė":u"Šilutės miestas",
        u"Širvintos":u"Širvintų miestas",
        u"Švenčionys":u"Švenčionių miestas",
        u"Švenčionėliai":u"Švenčionėlių miestas",
        u"Žagarė":u"Žagarės miestas",
        u"Žemaičių Naumiestis":u"Žemaičių Naumiesčio miestas",
        u"Žiežmariai":u"Žiežmarių miestas",
    }
    if not cities.has_key(city) :
        return city

    newcity = cities[city]
    #print "substituting %s to %s" %(city, newcity)
    return newcity





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
            if count + 1 > toPrint:
                break
            count += 1
            if count + 1 <= fromPrint:
                continue
            pollingDistricts.append(pollingDistrict)
        return pollingDistricts



    def preFetchAllConstituencies(self, pollingDistricts):
        time = TimeMeasurer()
        # fetch all counties in pseudo batch,
        constituencies = {}

        for pol in pollingDistricts:
            if constituencies.has_key(pol.Constituency.nr) == False:
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
        if self.previousDBRowCount is None:
            self.previousDBRowCount = PollingDistrictStreet.objects.count()

        # if we have none rows, then just return list, and do any checks,
        # no need to do that, right
        if self.previousDBRowCount == 0:
            return expandedStreets

        # will execute lots of selects against database
        # it will be very slow, but works for now
        for expandedStreet in expandedStreets:
            query = PollingDistrictStreet.objects.filter(institution = pollingDistrict.Constituency)
            query = query.filter(city = street.cityName)
            query = query.filter(street = expandedStreet.street)
            query = query.filter(pollingDistrict = pollingDistrict.PollingDistrict)
            query = query.filter(numberFrom = expandedStreet.numberFrom)
            query = query.filter(numberTo = expandedStreet.numberTo)
            #print query.query
            results = list(query)

            if len(results) == 0:
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
            if args[0].find(":") > 0:
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
                    pollingDistrictStreet.institution = pollingDistrict.Constituency
                    pollingDistrictStreet.municipality = changeMunicipalityToCorrectForm(pollingDistrict.District)
                    pollingDistrictStreet.city = changeToGenitiveCityName(street.cityName)
                    expandedStreetStr = expandedStreet.street
                    if expandedStreetStr == u"V. Druskio gatvė":
                        expandedStreetStr = u"Virginijaus Druskio gatvė"
                    pollingDistrictStreet.street = expandedStreetStr
                    pollingDistrictStreet.numberFrom =  expandedStreet.numberFrom
                    pollingDistrictStreet.numberTo = expandedStreet.numberTo
                    if (expandedStreet.numberFrom is not None):
                        pollingDistrictStreet.numberOdd = isHouseNumberOdd(expandedStreet.numberFrom)
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
