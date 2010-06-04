#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.test import TestCase
from ..imp import *
import os


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestImportLithuanianCounties(TestCase):
    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"
    alytusRecordFile = scriptPath + "/AlytausMiestas.txt"
    allRecords = scriptPath + "/Apygardos.txt"



    def countNumberOfRecords(self, fileName):
        file = open(fileName, "r")
        importer = LithuanianCountyReader(file)
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

    def test_Akmenes_read_record(self):

        file = open(self.singleRecordFile, "r")
        importer = LithuanianCountyReader(file)
        for loc in importer.getLocations():
            self.assertEqual(loc.District, "Akmenės rajonAS")
            self.assertEqual(loc.County, "Akmenės–Joniškio rinkimų apygarda Nr. 39")
            self.assertEqual(loc.ElectionDistrict, "Senamiesčio rinkimų apylinkė Nr. 1")
            self.assertTrue(loc.Addresses.index("Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs.,") >= 0)