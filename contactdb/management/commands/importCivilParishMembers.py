#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import LithuanianMPsReader, CivilParishMembersReader
from contactdb.models import HierarchicalGeoData, CivilParishMember
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException

class ImportCivilParishMemberException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian CivilParishMembers / seniūnai'


    def alreadyExists(self, name, surname):
        try:
            CivilParishMember.objects.get(name = name, surname = surname)
        except ObjectDoesNotExist:
            return False
        return True


    @transaction.commit_on_success
    def handle(self, *args, **options):
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianCivilParishMembers)
        reader = CivilParishMembersReader(fileName)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        count = 0

        for member in reader.ReadMembers():

            # check if already such member exists. Name and surname are primary keys
            if (self.alreadyExists(member.name, member.surname) == True):
                print "member %s %s already exists, CivilParish %s %d " % (member.name, member.surname, member.civilParish.name)
                continue

            # if does not exist, create it
            # relate existing constituency to an MP
            try:
                member.civilParish = HierarchicalGeoData.objects.get(name = member.civilParishStr, type = HierarchicalGeoData.HierarchicalGeoDataType[3][1])
            except ObjectDoesNotExist:
                raise ImportCivilParishMemberException("""Parish with name '%s' and type %s could not be found in database. Either the database is
not yet populated with Parish, or it is missing (probably because import data does not contain it)""" % \
                    (member.civilParishStr, HierarchicalGeoData.HierarchicalGeoDataType[3][1]))


            member.save()
            print (u"Imported parish member %s %s %s" % (member.name, member.surname, member.civilParish.text))
            count += 1
            if (count >= numberToPrint):
                break;
        print "succesfully imported %d Parish Members" % (count)