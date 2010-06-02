import os
from parasykjiems.contactdb.models import *

def ReadLine(file):
    return file.readline().strip("/n")

def ReadParliamentMembers(file):
    """A generator which returns parliament member instances from
given file"""
    header = ReadLine(file)

    for line in file:
        if (line == ""):
            break
        fields = line.split("\t")

        member = ParliamentMember()
        member.electoralDistrict = fields[0]
        member.name = fields[2]
        member.surname = fields[1]
        member.email = fields[6]
        yield member

#file = open("parliament members.txt", "r")
#for p in ReadParliamentMembers(file):
#    print p