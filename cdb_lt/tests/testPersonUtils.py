#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *
from cdb_lt.personUtils import splitIntoNameAndSurname

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )


class TestSpitFullName(TestCase):
    def setUp(self):
        pass

    def testsplitIntoNameAndSurname(self):
        self.assertEqual((u"Vardenis", u"Pavardenis"), splitIntoNameAndSurname(u"Vardenis Pavardenis"))
        self.assertEqual((u"Vardenis", u"Pavardenis"), splitIntoNameAndSurname(u"Vardenis Pavardenis "))
        self.assertEqual((u"V", u"Pavardenis"), splitIntoNameAndSurname(u"V. Pavardenis"))
        self.assertEqual((u"V", u"Pavardenis"), splitIntoNameAndSurname(u"V.Pavardenis"))
        self.assertEqual((u"Vardenis", u"Pavardenis Pavardauskas"), splitIntoNameAndSurname(u"Vardenis Pavardenis Pavardauskas"))
