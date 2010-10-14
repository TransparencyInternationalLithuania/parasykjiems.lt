#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pjutils.exc import ChainnedException
from contactdb.imp import LithuanianConstituencyParser
from django.core.exceptions import ObjectDoesNotExist
import csv
from cdb_lt_municipality.models import MunicipalityMember
from cdb_lt_seniunaitija.models import SeniunaitijaMember
from cdb_lt_civilparish.models import CivilParishMember
from cdb_lt_mps.models import ParliamentMember


class ParliamentMemberImportError(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)


class MunicipalityMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadMembers(self):
        for row in self.dictReader:
            member = MunicipalityMember()
            member.name = unicode(row["name"].strip(), 'utf-8')
            member.surname = unicode(row["surname"].strip(), 'utf-8')
            member.email = row["e-mail"]
            member.email2 = row["e-mail2"]
            member.phone = row["telephonenumber"].strip()
            member.phone2 = row["telephonenumber2"].strip()
            member.mobilePhone = row["mobilenumber"].strip()
            member.address = row["address"].strip()
            member.municipalityStr = unicode(row["municipality"].strip(), 'utf-8')
            member.uniqueKey = row["uniquekeynotchangeable"]
            yield member



class SeniunaitijaStreetParser:

    def GetStreets(self, streetStr):
        str = streetStr.split(',')

        for s in str:
            yield s.strip() 

def toUnicode(str):
    return unicode(str, 'utf-8')

class SeniunaitijaMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")

    def ReadMembers(self):
        for row in self.dictReader:
            member = SeniunaitijaMember()
            member.name = unicode(row["name"].strip(), 'utf-8')
            member.surname = unicode(row["surname"].strip(), 'utf-8')
            member.email = row["e-mail"]
            member.phone = row["telephonenumber"]
            member.homePhone = row["hometelephonenumber"]
            member.role = row["pareigos"]
            member.seniunaitijaStr = toUnicode(row["seniunaitija"].strip())
            member.territoryStr = toUnicode(row["territorycoveredbyseniunaitija"].strip())
            member.uniqueKey = int(row["uniquekeynotchangeable"])
            yield member

class CivilParishMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadMembers(self):
        for row in self.dictReader:
            member = CivilParishMember()
            member.name = unicode(row["name"].strip(), 'utf-8')
            member.surname = unicode(row["surname"].strip(), 'utf-8')
            #member.email = row["e-mail"]
            member.personalPhone = row["personaltelephonenumber"].strip()
            member.officeEmail = row["officee-mail"].strip()
            member.officePhone = row["officetelephonenumber"].strip()
            member.officeAddress = row["officeaddress"].strip()
            member.civilParishStr = unicode(row["institution"].strip(), 'utf-8')
            member.uniqueKey = row["uniquekeynotchangeable"]

            yield member


class LithuanianMPsReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadParliamentMembers(self):
        """A generator which returns parliament member instances from
    given file.  A constituency object is fetched from the database for this specific MP"""

        parser = LithuanianConstituencyParser()

        for row in self.dictReader:


            member = ParliamentMember()
            member.constituency = parser.ExtractConstituencyFromMPsFile(row["electoraldistrict"])
            member.name = unicode(row["name"], 'utf-8')
            member.surname = unicode(row["surname"], 'utf-8')
            member.email = row["e-mail"]
            member.uniqueKey = row["uniquekeynotchangeable"]

            yield member