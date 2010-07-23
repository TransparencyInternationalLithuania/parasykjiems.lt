
from contactdb.models import Constituency, CivilParishMember
from pjutils.exc import ChainnedException
from contactdb.imp import LithuanianConstituencyParser
from django.core.exceptions import ObjectDoesNotExist
import csv



class ParliamentMemberImportError(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)


class CivilParishMembersReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadMembers(self):
        for row in self.dictReader:
            member = CivilParishMember()
            member.name = row["name"]
            member.surname = row["surname"]
            #member.email = row["e-mail"]
            member.personalPhone = row["personaltelephonenumber"]
            member.officeEmail = row["officee-mail"]
            member.officePhone = row["officetelephonenumber"]
            member.officeAddress = row["officeaddress"]
            member.civilParishStr = row["institution"]
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
            member.name = row["name"]
            member.surname = row["surname"]
            member.email = row["e-mail"]

            yield member