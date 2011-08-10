#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test.testcases import TestCase
import os
from cdb_lt.mpStreetReader import LithuanianConstituencyReader, LithuanianConstituencyParser

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestImportLithuanianCounties(TestCase):
    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"
    alytusRecordFile = scriptPath + "/AlytausMiestas.txt"
    allRecords = scriptPath + "/Apygardos.txt"



    def countNumberOfRecords(self, fileName):
        file = open(fileName, "r")
        importer = LithuanianConstituencyReader(file)
        count = 0
        for l in importer.getLocations():
            count += 1
        return count

    def test_AllRecors_count(self):
        self.assertEqual(self.countNumberOfRecords(self.allRecords), 2034)

    def test_Alytaus_count(self):
        self.assertEqual(self.countNumberOfRecords(self.alytusRecordFile), 24)

    def test_Akmenes_count(self):
        self.assertEqual(self.countNumberOfRecords(self.singleRecordFile), 1)

    def assertPollingDistrict(self, allPollingDistricts, pollingDistrict, constituency, district,
                              pollingDistrictAddress = None, numberOfVoters = None):

        parser = LithuanianConstituencyParser()
        constituency = parser.ExtractConstituencyFromConstituencyFile(constituency)

        pd = allPollingDistricts[self.getKey(pollingDistrict, constituency)]
        if (pd == None):
            self.fail("Could not find polling district %s" % pollingDistrict)

        self.assertEqual(constituency.nr, pd.Constituency.nr)
        self.assertEqual(constituency.name, pd.Constituency.name)
        self.assertEqual(pollingDistrict, pd.PollingDistrict)
        self.assertEqual(district, pd.District)

        if (pollingDistrictAddress is not None):
            self.assertEqual(pollingDistrictAddress, pd.pollingDistrictAddress)

        if (numberOfVoters is not None):
            self.assertEqual(numberOfVoters, pd.numberOfVoters)


    def getKey(self, pollingDistrict, constituency):
        return "%s - %s %d" % (pollingDistrict, constituency.name, constituency.nr)

    def test_DistrictNames(self):
        # find a polling district and assert that district is correct
        allPollingDistricts = {}
        file = open(self.allRecords, "r")

        # probably this line can be even further reduced in length, help would be welcome
        for pollingDistrict in LithuanianConstituencyReader(file).getLocations():
            allPollingDistricts[self.getKey(pollingDistrict.PollingDistrict, pollingDistrict.Constituency)] = pollingDistrict

        self.assertPollingDistrict  (allPollingDistricts, u"Senamiesčio rinkimų apylinkė Nr. 1", u"Akmenės–Joniškio rinkimų apygarda Nr. 39", u"Akmenės rajonAS", u"Adresas *Vytauto g. 3, Naujoji Akmenė.", u"Rinkėjų skaičius *2632.")
        self.assertPollingDistrict(allPollingDistricts, u"Lomenos rinkimų apylinkė Nr. 4", u"Kaišiadorių–Elektrėnų rinkimų apygarda Nr. 59", u"Kaišiadorių rajonAS")
        self.assertPollingDistrict(allPollingDistricts, u"Girelės rinkimų apylinkė Nr. 3", u"Kaišiadorių–Elektrėnų rinkimų apygarda Nr. 59", u"Kaišiadorių rajonAS", u"Adresas *Girelės g. 53, Kaišiadorys, Technologijų ir verslo mokyklos bendrabučio salė.", u"Rinkėjų skaičius *2789.")

        self.assertPollingDistrict(allPollingDistricts, u"S. Daukanto rinkimų apylinkė Nr. 64", u"Danės rinkimų apygarda Nr. 19", u"Klaipėdos miestas", u"Adresas *S.Daukanto g. 5, Klaipėda.", u"Rinkėjų skaičius *1001.")



    def test_Akmenes_read_record(self):

        file = open(self.singleRecordFile, "r")
        importer = LithuanianConstituencyReader(file)
        for loc in importer.getLocations():
            self.assertEqual(loc.District, u"Akmenės rajonAS")
            self.assertEqual(loc.Constituency.name, u"Akmenės–Joniškio rinkimų apygarda")
            self.assertEqual(loc.Constituency.nr, 39)
            self.assertEqual(loc.PollingDistrict, u"Senamiesčio rinkimų apylinkė Nr. 1")
            self.assertTrue(loc.Addresses.index(u"Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs.,") >= 0)
