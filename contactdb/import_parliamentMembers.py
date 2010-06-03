
from contactdb.models import ParliamentMember
from contactdb.tests.exc import ChainnedException


class ParliamentMemberImportError(ChainnedException):
    def __init__(self, message, inner = None):
        ChainnedException.__init__(self, message, inner)



def ReadLine(file):
    return file.readline().strip("/n")

def readField(fields, index):
    if (index >= len(fields)):
        return ""
    return fields[index]

def ReadParliamentMembers(file):
    """A generator which returns parliament member instances from
given file"""
    header = ReadLine(file)

    count = 0
    for line in file:
        if (line == ""):
            break
        count += 1 
        fields = line.split("\t")


        member = ParliamentMember()
        member.electoralDistrict = readField(fields, 0)
        member.name = readField(fields, 2)
        member.surname = readField(fields, 1)
        member.email = readField(fields, 6)

        try:
            validateMember(member)
        except ParliamentMemberImportError as e:
            raise ParliamentMemberImportError("error importing line \n %(lineNumber)s \n %(line)s" % {'lineNumber' : count, 'line': line}, e)

        yield member

def validateMember(member):
    if member.electoralDistrict.lower().find("nr") < 0:
        raise ParliamentMemberImportError("ElectoralDistrict field does not contain number. It was '%(fieldName)s', and it did not contain letters 'nr' See stack trace for more details" % {'fieldName' : member.electoralDistrict})


#file = open("parliament members.txt", "r")
#for p in ReadParliamentMembers(file):
#    print p