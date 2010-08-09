#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contactdb.models import MunicipalityMember, SeniunaitijaMember, ParliamentMember, CivilParishMember
from pjutils.exc import ChainnedException
from contactdb.imp import LithuanianConstituencyParser
from django.core.exceptions import ObjectDoesNotExist
import csv



class ParliamentMemberImportError(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)


class MunicipalityMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadMembers(self):
        for row in self.dictReader:
            member = MunicipalityMember()
            member.name = row["name"].strip()
            member.surname = row["surname"].strip()
            member.email = row["e-mail"]
            member.phone = row["telephonenumber"].strip()
            member.mobilePhone = row["mobilenumber"].strip()
            member.address = row["address"].strip()
            member.municipalityStr = row["municipality"].strip()
            member.uniqueKey = row["uniquekeynotchangeable"]
            yield member



class SeniunaitijaStreetParser:

    def GetStreets(self, streetStr):
        str = streetStr.split(',')

        for s in str:
            yield s.strip() 



class SeniunaitijaMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")

    def ReadMembers(self):
        for row in self.dictReader:
            member = SeniunaitijaMember()
            member.name = row["name"].strip()
            member.surname = row["surname"].strip()
            member.email = row["e-mail"]
            member.role = row["pareigos"]
            member.seniunaitijaStr = row["seniūnaitija"].strip()
            member.uniqueKey = row["uniquekeynotchangeable"]
            yield member

class CivilParishMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadMembers(self):
        for row in self.dictReader:
            member = CivilParishMember()
            member.name = row["name"].strip()
            member.surname = row["surname"].strip()
            #member.email = row["e-mail"]
            member.personalPhone = row["personaltelephonenumber"].strip()
            member.officeEmail = row["officee-mail"].strip()
            member.officePhone = row["officetelephonenumber"].strip()
            member.officeAddress = row["officeaddress"].strip()
            member.civilParishStr = row["institution"].strip()
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
            member.email = unicode(row["e-mail"], 'utf-8')
            member.uniqueKey = unicode(row["uniquekeynotchangeable"], 'utf-8')

            yield member