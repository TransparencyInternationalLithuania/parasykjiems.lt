#!/usr/bin/env python
# -*- coding: utf8 -*-


from django.test import TestCase
import os
from contactdb.import_parliamentMembers import ReadParliamentMembers


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestReadParliamentMembers(TestCase):
    allRecords = scriptPath + "/parliament members.txt"

    def countNumberOfRecords(self, fileName):
        file = open(fileName, "r")
        count = 0
        for l in ReadParliamentMembers(file):
            count += 1
        return count

    def test_AllRecors_count(self):
        self.assertEqual(self.countNumberOfRecords(self.allRecords), 71)

    def test_Read_first_record(self):

        file = open(self.allRecords, "r")
        for loc in ReadParliamentMembers(file):
            self.assertEqual(loc.electoralDistrict, "Naujamiesčio (Nr. 1)")
            self.assertEqual(loc.name, "Irena")
            self.assertEqual(loc.surname, "Degutienė")
            self.assertEqual(loc.email, "Irena.Degutiene@lrs.lt, irdegu@lrs.lt")
            break;