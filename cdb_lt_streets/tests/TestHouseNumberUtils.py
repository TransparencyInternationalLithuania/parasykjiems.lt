#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_streets.houseNumberUtils import ContainsHouseNumbers, padHouseNumberWithZeroes, depadHouseNumberWithZeroes, isHouseNumberOdd
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )


class TestIsHouseNumberOdd(TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        self.assertEqual(True, isHouseNumberOdd(1))
        self.assertEqual(None, isHouseNumberOdd(""))
        self.assertEqual(None, isHouseNumberOdd(None))



class TestContainsHouseNumbers(TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        self.assertEqual(True, ContainsHouseNumbers("Gedimino 9a"))

    def testBasic2(self):
        self.assertEqual(False, ContainsHouseNumbers("Gedimino 9-"))

    def testBasic2(self):
        self.assertEqual(False, ContainsHouseNumbers("Sausio 13-osios g."))
        self.assertEqual(True, ContainsHouseNumbers("Sausio 13-osios g. 5"))


class TestPadHouseNumberWithZeroes(TestCase):
    def setUp(self):
        pass

    def testBasic(self):
        self.assertEqual(u"", padHouseNumberWithZeroes(u""))
        self.assertEqual(u"00010", padHouseNumberWithZeroes(u"1"))
        self.assertEqual(u"00110", padHouseNumberWithZeroes(u"11"))
        self.assertEqual(u"00150", padHouseNumberWithZeroes(15))
        self.assertEqual(u"0001A", padHouseNumberWithZeroes(u"1A"))

        # convert letter to uppercaes
        self.assertEqual(u"0001A", padHouseNumberWithZeroes(u"1a"))

    def testDePad(self):
        self.assertEqual(u"1", depadHouseNumberWithZeroes(u"00010"))
        self.assertEqual(u"100", depadHouseNumberWithZeroes(u"01000"))
        self.assertEqual(u"100a", depadHouseNumberWithZeroes(u"0100a"))


