#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
from cdb_lt_municipality.models import Municipality
from pjutils.timemeasurement import TimeMeasurer

class ImportMunicipalityMemberException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian MunicipalityMembers / Mayors'


    @transaction.commit_on_success
    def handle(self, *args, **options):
        fileName = ImportSources.LithuanianMunicipalities
        print u"Import street index data from csv file %s" % fileName
        ImportSources.EsnureExists(ImportSources.LithuanianMunicipalities)
        elapsedTime = TimeMeasurer()

        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")

        self.count = 0

        for row in self.dictReader:
            self.count += 1
            id = int(unicode(row["id"].strip(), 'utf-8'))
            municipality = unicode(row["municipality"].strip(), 'utf-8')

            municipalities = Municipality()
            municipalities.id = id
            municipalities.name = municipality
            municipalities.save()


        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"finished, written total %s lines" % self.count