#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import SeniunaitijaMembersReader
from contactdb.models import HierarchicalGeoData, SeniunaitijaMember
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
import os
import csv
from pjutils.exc import ChainnedException
from contactdb.management.commands.importCivilParishMembers import ImportCivilParishMemberException

class ImportSeniunaitijaMemberException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian SeniunaitijaMember  / seniūnaičiai'


    def alreadyExists(self, member):
        try:
            return SeniunaitijaMember.objects.get(uniqueKey = member.uniqueKey)
        except ObjectDoesNotExist:
            return None


    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianSeniunaitijaMembers)
        fileName = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)
        reader = SeniunaitijaMembersReader(fileName)

        maxNumberToImport = 9999
        if len(args) > 0:
            maxNumberToImport = int(args[0])

        count = 0

        for member in reader.ReadMembers():

            if (member.name.strip() == ""):
                print "member name was empty. "
                print "Probably that means that in seniunaitija %s a member was not yet elected" % member.seniunaitijaStr

            # check if already such member exists. Name and surname are primary keys
            m = self.alreadyExists(member)
            if (m is not None):
                print "already exists: %s %s %s " % (m.name, m.surname, m.seniunaitija.name)
                continue

            # if does not exist, create it
            # relate existing seniunaitija to an MP
            try:
                type = HierarchicalGeoData.HierarchicalGeoDataType.Seniunaitija
                name = member.seniunaitijaStr
                #print "query: %s" % HierarchicalGeoData.objects.filter(name__contains = name).filter(type = type)[0:1].query
                member.seniunaitija = HierarchicalGeoData.objects.filter(name__contains = name).filter(type = type)[0:1].get()
            except ObjectDoesNotExist:
                raise ImportCivilParishMemberException("""Seniunaitija with name '%s' and type '%s' could not be found in database. Either the database is
not yet populated with seniunaitija, or it is missing (probably because import data does not contain it)""" % \
                    (name, type))


            member.save()
            print (u"Imported seniunaitija member %s %s %s" % (member.name, member.surname, member.seniunaitija.name))
            count += 1
            if (count >= maxNumberToImport):
                break
        print "succesfully imported %d seniunaitija members" % (count)