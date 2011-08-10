#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import sys

from django.core.management.base import BaseCommand
from django.core import management
import os
from django.db import transaction
from pjutils import uniconsole
from contactdb.models import InstitutionType
from territories.houseNumberUtils import depadHouseNumberWithZeroes
from territories.models import InstitutionTerritory, CountryAddresses

class Command(BaseCommand):
    args = '<>'
    help = """Searches for members against hand-written list of addresses and checks whether exactly 1 representative is returned"""


    def addKey(self, key):
        if self.distinct.has_key(key) == False:
            self.distinct[key] = ""
            self.streets.append(key)


    @transaction.commit_on_success
    def handle(self, *args, **options):
        self.distinct = {}

        municipalities = [u"Vilniaus miesto savivaldybė", u"Klaipėdos miesto savivaldybė", u"Kauno miesto savivaldybė"]

        self.streets = []

        for t in CountryAddresses.objects.all().filter(municipality__in=municipalities).order_by(u"municipality", u"city", u"street"):
            if t.city == u"":
                continue
            if t.street != u"":
                if hasattr(t, "numberFrom"):
                    t.numberFrom = depadHouseNumberWithZeroes(t.numberFrom)
                    t.numberTo = depadHouseNumberWithZeroes(t.numberTo)
                    if t.numberFrom != u"":
                        key = "%s %s, %s, %s" % (t.street, t.numberFrom, t.city, t.municipality)
                        self.addKey(key)

                    if t.numberTo != u"" and t.numberTo.find("999") < 0:
                        key = "%s %s, %s, %s" % (t.street, t.numberTo, t.city, t.municipality)
                        self.addKey(key)

                    if t.numberFrom == u"":
                        key = "%s, %s, %s" % (t.street, t.city, t.municipality)
                        self.addKey(key)
                else:
                    key = "%s, %s, %s" % (t.street, t.city, t.municipality)
                    self.addKey(key)

            else:
                if t.civilParish != u"":
                    key = "%s, %s, %s" % (t.city, t.civilParish, t.municipality)
                    self.addKey(key)
                else:
                    key = "%s, %s" % (t.city, t.municipality)
                    self.addKey(key)




        for v in self.streets:
            print v




