#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand
import logging
from cdb_lt_streets.crawlers.LRValstybe_lt.lrvalstybe_csvoutput import LRValstybeCsvOut, yieldCivilParishHeadMembers
from pjutils.uniconsole import *

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<>'
    help = """"""

    def handle(self, *args, **options):
        headers = [u"fullname", u"email", u"municipality", u"civilparish", u"officephone", u"officeaddress", u"title", u"comments"]
        out = LRValstybeCsvOut(headers=headers)
        out.writeHeader()

        for member in yieldCivilParishHeadMembers():
            out.printSingleContact(member)
