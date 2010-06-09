from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import LithuanianMPsReader
from contactdb.models import ParliamentMember, County
from contactdb.imp import ImportSources
import os

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian parliament members'


    def alreadyExists(self, parliamentMember):
        try:
            ParliamentMember.objects.get(name = parliamentMember.name, surname = parliamentMember.surname)
        except ObjectDoesNotExist:
            return False
        return True


    def handle(self, *args, **options):
        allRecords = os.getcwd() + ImportSources.LithuanianMPs
        file = open(allRecords, "r")
        reader = LithuanianMPsReader(file)

        numberToPrint = 9999
        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0


        for member in reader.ReadParliamentMembers():

            # check if already such member exists. Name and surname are primary keys
            if (self.alreadyExists(member) == True):
                print "member %s %s already exists, County %s %d " % (member.name, member.surname, member.county.name, member.county.nr)
                continue

            # if does not exist, create it


            # relate existing county to an MP
            try:
                member.county = County.objects.get(nr = member.county.nr)
            except ObjectDoesNotExist:
                print "County with nr '%d' could not be found in database. Either the database is not yet populated with Counties, or it is missing (probably because import data does not contain it)" % (member.county.nr)
                print "Skipping this MPs. Continuing with the rest"
                continue


            member.save()
            print (u"Imported MP %s %s, County %s %d" % (member.name, member.surname, member.county.name, member.county.nr)).encode('utf-8')
            count += 1
            if (count >= numberToPrint):
                break;
        print "succesfully imported %d MPs" % (count)