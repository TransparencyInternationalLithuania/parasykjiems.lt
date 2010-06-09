
from contactdb.models import ParliamentMember
from contactdb.exc import ChainnedException


class ParliamentMemberImportError(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)

class LithuanianMPsReader:
    def __init__(self, file):
        self.file = file

    def ReadLine(self):
        return self.file.readline().strip("/n")

    def readField(self, fields, index):
        if (index >= len(fields)):
            return ""
        return fields[index]

    def ReadParliamentMembers(self):
        """A generator which returns parliament member instances from
    given file"""
        header = self.ReadLine()

        count = 0
        for line in self.file:
            if (line == ""):
                break
            count += 1
            fields = line.split("\t")


            member = ParliamentMember()
            member.electoralDistrict = self.readField(fields, 0)
            member.name = self.readField(fields, 2)
            member.surname = self.readField(fields, 1)
            member.email = self.readField(fields, 6)

            try:
                self.validateMember(member)
            except ParliamentMemberImportError as e:
                raise ParliamentMemberImportError("error importing line \n %(lineNumber)s \n %(line)s" % {'lineNumber' : count, 'line': line}, e)

            yield member

    def validateMember(self, member):
        if member.electoralDistrict.lower().find("nr") < 0:
            raise ParliamentMemberImportError("ElectoralDistrict field does not contain number. It was '%(fieldName)s', and it did not contain letters 'nr' See stack trace for more details" % {'fieldName' : member.electoralDistrict})


#file = open("parliament members.txt", "r")
#for p in ReadParliamentMembers(file):
#    print p