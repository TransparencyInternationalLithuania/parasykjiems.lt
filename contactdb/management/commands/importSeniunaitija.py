#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import SeniunaitijaMembersReader, SeniunaitijaStreetParser
from contactdb.models import HierarchicalGeoData, SeniunaitijaMember
from contactdb.imp import ImportSources, GoogleDocsSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
from contactdb.management.commands.importCivilParishMembers import ImportCivilParishMemberException
from contactdb.LTRegisterCenter.webparser import LTGeoDataHierarchy
from contactdb.imp import GoogleDocsSources
import logging

class ImportSeniunaitijaException(ChainnedException):
    pass

class SeniunaitijaNotFoundException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian Seniunaitija / seniūnaitijos'

    def _GetCivilParish(self):
        # find a civilParish object
        try:
            # TODO: how to do a normal method chaining in Python so that line would not be that long??
            civilParish = HierarchicalGeoData.objects.filter(name__contains = self.civilParishStr).filter(type = HierarchicalGeoData.HierarchicalGeoDataType.CivilParish).filter(parent__name__contains = self.municipalityStr).get()
        except HierarchicalGeoData.DoesNotExist:
            str = """Could not find Civil parish with name '%s' and type '%s'. \n Municipality '%s'
Database table: %s. Data source taken from GoogleDoc '%s'. Unique key '%s' """ % \
                (self.civilParishStr, HierarchicalGeoData.HierarchicalGeoDataType.CivilParish, self.municipalityStr,
                HierarchicalGeoData.objects.model._meta.db_table, GoogleDocsSources.LithuanianSeniunaitijaMembers,
                self.uniqueKey)
            logging.error(str)
            raise SeniunaitijaNotFoundException(str)
        except HierarchicalGeoData.MultipleObjectsReturned:
            raise ImportSeniunaitijaException("Found multiple Civil parish with name '%s' and type '%s'. \n Municipality '%s'" % (self.civilParishStr, HierarchicalGeoData.HierarchicalGeoDataType.CivilParish, self.municipalityStr))
        return civilParish


    def _GetOrCreateSeniunaitija(self):
        seniunaitija = HierarchicalGeoData.FindByName(self.seniunaitijaStr, type = HierarchicalGeoData.HierarchicalGeoDataType.Seniunaitija, parentName = self.civilParishStr)

        if (seniunaitija is None):
            civilParish = self._GetCivilParish()

            seniunaitija = HierarchicalGeoData()
            seniunaitija.name = self.seniunaitijaStr
            seniunaitija.parent = civilParish
            seniunaitija.type = HierarchicalGeoData.HierarchicalGeoDataType.Seniunaitija
            seniunaitija.save()
            print "creating new Seniunatija object %s %s" % (self.seniunaitijaStr, civilParish.name)
        else:
            print "already exists Seniunatija object %s %s " % (self.seniunaitijaStr, self.civilParishStr)
        return seniunaitija


    @transaction.commit_on_success
    def handle(self, *args, **options):
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        parser = SeniunaitijaStreetParser()

        count = 0
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")

        try:
            for row in self.dictReader:
                # i use class instance variables here on purpose. Might be tricky if the class grows too much,
                # but handy for now

                self.seniunaitijaStr = unicode(row["seniunaitija"].strip(), 'utf-8')
                self.civilParishStr = unicode(row["townshipseniunija"].strip(), 'utf-8')
                streets = unicode(row["territorycoveredbyseniunaitija"].strip(), 'utf-8')
                self.municipalityStr = unicode(row["municipality"].strip(), 'utf-8')
                self.uniqueKey = row["uniquekeynotchangeable"].strip()


                # skip empty entries
                if (self.seniunaitijaStr == ""):
                    continue
                # remove some keywords from strings, and add others
                # this is to conform to a de-facto data naming standard
                self.municipalityStr = self.municipalityStr.replace("rajono", "").strip()
                if (self.civilParishStr.find(u"seniūnija") < 0):
                    self.civilParishStr = u"%s seniūnija" % self.civilParishStr


                # check that current Seniunaitija object does not already exist
                seniunaitija = self._GetOrCreateSeniunaitija()

                # no importin of streets so far
                #for s in parser.GetStreets(streets):
                #    print s



                count += 1
                if (count >= maxNumberToImport):
                    break
        except SeniunaitijaNotFoundException as e:
            raise ImportSeniunaitijaException("""
Seniunaitija was not found in HierarchicalGeoData. That probabl means that hierarchical geo data was not yet
imported. Issue this command to import    \n:  ltGeoDataImport --max-depth 3
Another option is that the data is wrong, such as a misspeled Seniunaitija name""", e)

        print "succesfully imported %d seniunaitija" % (count)