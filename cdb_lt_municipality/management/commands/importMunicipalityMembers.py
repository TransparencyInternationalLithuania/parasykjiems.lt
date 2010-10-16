#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import MunicipalityMembersReader
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
from cdb_lt_municipality.models import MunicipalityMember, Municipality

class ImportMunicipalityMemberException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian MunicipalityMembers / Mayors'


    def alreadyExists(self, member):
        try:
            return MunicipalityMember.objects.get(uniqueKey = member.uniqueKey)
        except ObjectDoesNotExist:
            return None


    #@transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianMunicipalityMembers)
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianMunicipalityMembers)
        reader = MunicipalityMembersReader(fileName)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        count = 0

        for member in reader.ReadMembers():
            if (member.name.strip() == ""):
                continue

            # check if already such member exists. Name and surname are primary keys
            m = self.alreadyExists(member)
            # relate existing constituency to an MP
            try:
                name = member.municipalityStr.strip()
                #name = name.replace(u'rajono', '')
                name = u"%s savivaldybė" % (name)
                member.municipality = Municipality.objects.filter(name__contains=name)[0:1].get()
            except ObjectDoesNotExist:
                raise ImportMunicipalityMemberException("""Municipality with name '%s' and type '%s' could not be found in database. Either the database is
not yet populated with Municipalities, or it is missing (probably because import data does not contain it)""" % \
                    (name, type))


            if (m is None):
                print (u"Importing municipality member %s %s %s" % (member.name, member.surname, member.uniqueKey))
            else:
                member.id = m.id
                print u"updating Municipality member: %s %s %s " % (m.name, m.surname, m.uniqueKey)

            member.save()

            count += 1
            if (count >= maxNumberToImport):
                break
        print u"succesfully imported / updated %d municipality Members" % (count)