from django.test import TestCase
from parasykjiems.contactdb.imp import *
import os


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class SimpleTest(TestCase):
    singleRecordFile = scriptPath + "/a.txt"

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

    def test_read_single_record_count(self):
        file = open(self.singleRecordFile, "r")
        count = 0
        for l in getLocations(file):
            count += 1

        self.assertEqual(count, 1)

    def test_read_single_record(self):

        file = open(self.singleRecordFile, "r")
        for loc in getLocations(file):
            self.assertEqual(loc.District, "Akmenės rajonAS")
            self.assertEqual(loc.County, "Akmenės–Joniškio rinkimų apygarda Nr. 39")
            self.assertEqual(loc.ElectionDistrict, "Senamiesčio rinkimų apylinkė Nr. 1")
            self.assertTrue(loc.Addresses.index("Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs.,") >= 0)




