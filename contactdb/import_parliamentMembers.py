#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pjutils.exc import ChainnedException
import csv
from cdb_lt_municipality.models import MunicipalityMember
from cdb_lt_seniunaitija.models import SeniunaitijaMember
from cdb_lt_civilparish.models import CivilParishMember


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




def toUnicode(str):
    return unicode(str, 'utf-8')



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
