from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import LithuanianMPsReader
from contactdb.models import ParliamentMember, Constituency
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
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


    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianMPs)
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianMPs)
        reader = LithuanianMPsReader(allRecords)

        numberToPrint = 9999
        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0


        for member in reader.ReadParliamentMembers():

            # check if already such member exists. Name and surname are primary keys
            if (self.alreadyExists(member) == True):
                print "member %s %s already exists, Constituency %s %d " % (member.name, member.surname, member.constituency.name, member.constituency.nr)
                continue

            # if does not exist, create it


            # relate existing constituency to an MP
            try:
                if (member.constituency is None):
                    member.constituency = None
                else:
                    member.constituency = Constituency.objects.get(nr = member.constituency.nr)
            except ObjectDoesNotExist:
                print "Constituency with nr '%d' could not be found in database. Either the database is not yet populated with contstituencies, or it is missing (probably because import data does not contain it)" % (member.constituency.nr)
                print "Skipping this MPs. Continuing with the rest"
                continue


            member.save()
            if (member.constituency is None):
                print "Imported MP %s %s" % (member.name, member.surname)
            else:
                print u"Imported MP %s %s, Constituency %s %d" % (member.name, member.surname, member.constituency.name, member.constituency.nr)
            count += 1
            if (count >= numberToPrint):
                break;
        print "succesfully imported %d MPs" % (count)