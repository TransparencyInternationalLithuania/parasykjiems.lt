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


    def alreadyExists(self, member):
        try:
            return CivilParishMember.objects.get(uniqueKey = member.uniqueKey)
        except ObjectDoesNotExist:
            return None


    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianCivilParishMembers)
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianCivilParishMembers)
        reader = CivilParishMembersReader(fileName)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        count = 0

        for member in reader.ReadMembers():

            if (member.name.strip() == ""):
                continue

            # check if already such member exists. Name and surname are primary keys
            m = self.alreadyExists(member)
            if (m is None):
                # if does not exist, create it
                # relate existing constituency to an MP
                try:
                    type = HierarchicalGeoData.HierarchicalGeoDataType.CivilParish
                    name = member.civilParishStr
                    member.civilParish = HierarchicalGeoData.objects.filter(name = name).filter(type = type)[0:1].get()
                except ObjectDoesNotExist:
                    raise ImportCivilParishMemberException("""Parish with name '%s' and type '%s' could not be found in database. Either the database is
    not yet populated with Parish, or it is missing (probably because import data does not contain it)""" % \
                        (name, type))

                print (u"Imported parish member %s %s %s" % (member.name, member.surname, member.civilParish.name))
            else:
                member.id = m.id
                print "updating parish member: %s %s %s " % (m.name, m.surname, m.uniqueKey)


            member.save()

            count += 1
            if (count >= maxNumberToImport):
                break
        print "succesfully imported/updated %d Parish Members" % (count)