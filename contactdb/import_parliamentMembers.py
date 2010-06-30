
from contactdb.models import ParliamentMember, Constituency
from pjutils.exc import ChainnedException
from contactdb.imp import LithuanianConstituencyParser
from django.core.exceptions import ObjectDoesNotExist
import csv



class ParliamentMemberImportError(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)

class LithuanianMPsReader:
    def __init__(self, fileName):
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")


    def ReadParliamentMembers(self):
        """A generator which returns parliament member instances from
    given file.  A county object is fetched from the database for this specific MP"""

        parser = LithuanianConstituencyParser()

        count = 0
        for row in self.dictReader:
            count += 1


            member = ParliamentMember()
            member.county = parser.ExtractConstituencyFromMPsFile(row["electoraldistrict"])
            member.name = row["name"]
            member.surname = row["surname"]
            member.email = row["e-mail"]

            try:
                self.validateMember(member)
            except ParliamentMemberImportError as e:
                raise ParliamentMemberImportError("error importing line \n %(lineNumber)s \n %(line)s" % {'lineNumber' : count, 'line': line}, e)

            yield member

    def validateMember(self, member):
        return True


#file = open("parliament members.txt", "r")
#for p in ReadParliamentMembers(file):
#    print p