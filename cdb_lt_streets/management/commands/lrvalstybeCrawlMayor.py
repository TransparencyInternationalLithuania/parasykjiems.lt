#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand
import logging
from cdb_lt_streets.crawlers.LRValstybe_lt.lrvalstybe_csvoutput import printMayors
from pjutils.uniconsole import *

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = """Crawls part of Register Center page and saves data to csv files.  You can call command like
    ltGeoDataCrawl [2:5]  to start from second source and finish in fifth"""

    def handle(self, *args, **options):
        printMayors()
