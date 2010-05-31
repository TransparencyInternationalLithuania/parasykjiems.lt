from django.test import TestCase
from parasykjiems.contactdb.imp import *
import os


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class SimpleTest(TestCase):
    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"
    alytusRecordFile = scriptPath + "/AlytausMiestas.txt"
    allRecords = scriptPath + "/Apygardos.txt"

    def countNumberOfRecords(self, fileName):
        file = open(fileName, "r")
        count = 0
        for l in getLocations(file):
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
        for loc in getLocations(file):
            self.assertEqual(loc.District, "Akmenės rajonAS")
            self.assertEqual(loc.County, "Akmenės–Joniškio rinkimų apygarda Nr. 39")
            self.assertEqual(loc.ElectionDistrict, "Senamiesčio rinkimų apylinkė Nr. 1")
            self.assertTrue(loc.Addresses.index("Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs.,") >= 0)