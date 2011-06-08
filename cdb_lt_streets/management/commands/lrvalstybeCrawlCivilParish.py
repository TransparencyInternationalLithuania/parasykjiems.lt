#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand
import logging
from cdb_lt_streets.crawlers.LRValstybe_lt.lrvalstybe_csvoutput import printCivilParish
from pjutils.uniconsole import *

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<>'
    help = """"""

    def handle(self, *args, **options):
        printCivilParish()
