#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from cdb_lt_seniunaitija.management.commands.importSeniunaitija import SeniunaitijaStreetParser

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSeniunaitijaStreetParser(TestCase):
    parser = SeniunaitijaStreetParser()

    def AssureEqual(self, stringsListToTestAgainst, stringsToParse):
        count = 0
        for s in self.parser.GetStreets(stringsToParse):
            self.assertEqual(stringsListToTestAgainst[count], s)
            count += 1
    
    def test_ParseStreets1(self):
        str = ("Bardžių k.", "Bijotų k.", "Cipkiškių k.", "Kalniškių k.", "Kazokų k.", "Kumečių k.", "Padvarių k.", 
               "Pavėrių k.", "Poškakaimio k.", "Simėnų k.")

        s = "Bardžių k., Bijotų k., Cipkiškių k., Kalniškių k., Kazokų k., Kumečių k., Padvarių k., Pavėrių k., Poškakaimio k., Simėnų k."
        self.AssureEqual(str, s)