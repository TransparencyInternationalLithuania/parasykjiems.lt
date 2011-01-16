#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test.testcases import TestCase
import os
from cdb_lt_civilparish.management.commands.importCivilParishStreets_Kaunas import yieldRanges

class TestYieldHouseRanges(TestCase):
    def assertRangesEqual(self, fromNumber = None, toNumber = None, result = None):
        if (result is None):
            self.fail("Result was null, but we expect fromNumber to be %s" % fromNumber)

        self.assertEqual(fromNumber, result.numberFrom)
        self.assertEqual(toNumber, result.numberTo, msg="toNumber had to be %s, but was %s" % (toNumber, result.numberTo))
        isOdd = int(fromNumber) % 2 == 1
        self.assertEqual(isOdd, result.numberOdd)

    def test_single_range_odd(self):
        houseNumbers = ["1", "3", "11"]
        result = list(yieldRanges(houseNumbers))
        self.assertRangesEqual("1", "3", result = result[0])
        self.assertRangesEqual("11", result = result[1])
        self.assertEqual(2, len(result))

    def test_single_range_even(self):
        houseNumbers = ["0", "2", "10"]
        result = list(yieldRanges(houseNumbers))
        self.assertRangesEqual("0", "2", result = result[0])
        self.assertRangesEqual("10", result = result[1])
        self.assertEqual(2, len(result))

    def test_longer_range_even(self):
        houseNumbers = ["42", "44", "46", "48"]
        result = list(yieldRanges(houseNumbers))
        self.assertRangesEqual("42", "48", result = result[0])
        self.assertEqual(1, len(result))


