#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from cdb_lt_streets.models import LithuanianCases
from cdb_lt_streets.ltData import MunicipalityCases
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<speed>'
    help = """"""

    @transaction.commit_on_success
    def handle(self, *args, **options):
        print "Will import LithuanianCases for municipalities"
        for key, data in MunicipalityCases.iteritems():
            case = LithuanianCases()
            case.nominative = key
            case.genitive = data
            case.institutionType = LithuanianCases.Type.Municipality
            case.save()
        print "finished"

