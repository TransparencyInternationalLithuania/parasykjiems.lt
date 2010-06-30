#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.test import TestCase
import os
from contactdb.imp import LithuanianConstituencyParser, LithuanianConstituencyReader


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )


class TestLithuanianCountyParser(TestCase):
    parser = LithuanianConstituencyParser()

    def test_ExtractCountyFromCountyFile(self):
        county = self.parser.ExtractConstituencyFromCountyFile("Lazdynų rinkimų apygarda Nr. 9")
        self.assertEqual("Lazdynų rinkimų apygarda", county.name)
        self.assertEqual(9, county.nr)

    def test_ExtractCountyFromMPsFile(self):
        county = self.parser.ExtractConstituencyFromMPsFile("Naujamiesčio (Nr. 1)")
        self.assertEqual("Naujamiesčio", county.name)
        self.assertEqual(1, county.nr)


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
        constituency = parser.ExtractConstituencyFromCountyFile(constituency)

        pd = allPollingDistricts[self.getKey(pollingDistrict, constituency)]
        if (pd == None):
            self.fail("Could not find polling district %s" % pollingDistrict)

        self.assertEqual(constituency.nr, pd.County.nr)
        self.assertEqual(constituency.name, pd.County.name)
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
            allPollingDistricts[self.getKey(pollingDistrict.PollingDistrict, pollingDistrict.County)] = pollingDistrict

        self.assertPollingDistrict(allPollingDistricts, "Senamiesčio rinkimų apylinkė Nr. 1", "Akmenės–Joniškio rinkimų apygarda Nr. 39", "Akmenės rajonAS", "Adresas *Vytauto g. 3, Naujoji Akmenė.", "Rinkėjų skaičius *2632.")
        self.assertPollingDistrict(allPollingDistricts, "Lomenos rinkimų apylinkė Nr. 4", "Kaišiadorių–Elektrėnų rinkimų apygarda Nr. 59", "Kaišiadorių rajonAS")
        self.assertPollingDistrict(allPollingDistricts, "Girelės rinkimų apylinkė Nr. 3", "Kaišiadorių–Elektrėnų rinkimų apygarda Nr. 59", "Kaišiadorių rajonAS", "Adresas *Girelės g. 53, Kaišiadorys, Technologijų ir verslo mokyklos bendrabučio salė.", "Rinkėjų skaičius *2789.")

        self.assertPollingDistrict(allPollingDistricts, "S. Daukanto rinkimų apylinkė Nr. 64", "Danės rinkimų apygarda Nr. 19", "Klaipėdos miestas", "Adresas *S.Daukanto g. 5, Klaipėda.", "Rinkėjų skaičius *1001.")



    def test_Akmenes_read_record(self):

        file = open(self.singleRecordFile, "r")
        importer = LithuanianConstituencyReader(file)
        for loc in importer.getLocations():
            self.assertEqual(loc.District, "Akmenės rajonAS")
            self.assertEqual(loc.County.name, "Akmenės–Joniškio rinkimų apygarda")
            self.assertEqual(loc.County.nr, 39)
            self.assertEqual(loc.PollingDistrict, "Senamiesčio rinkimų apylinkė Nr. 1")
            self.assertTrue(loc.Addresses.index("Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs.,") >= 0)