from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from contactdb.import_parliamentMembers import LithuanianMPsReader
from contactdb.models import ParliamentMember, Constituency
from contactdb.imp import ImportSources
from django.db import transaction
from pjutils import uniconsole
import os
import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian parliament members'


    def alreadyExists(self, parliamentMember):
        try:
            return ParliamentMember.objects.get(uniqueKey = parliamentMember.uniqueKey)
        except ObjectDoesNotExist:
            return None

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

            # skipping empty members
            if (member.name.strip() == ""):
                continue

            # relate existing constituency to an MP
            try:
                if (member.constituency is None):
                    member.constituency = None
                else:
                    member.constituency = Constituency.objects.get(nr = member.constituency.nr)
            except ObjectDoesNotExist:
                print u"Constituency with nr '%d' could not be found in database. Either the database is not yet populated with contstituencies, or it is missing (probably because import data does not contain it)" % (member.constituency.nr)
                print u"Skipping this MPs. Continuing with the rest"
                continue

            # check if already such member exists. Name and surname are primary keys
            m = self.alreadyExists(member)
            if (m is None):
                print u"Imported MP %s %s %s" % (member.name, member.surname, member.uniqueKey)

            else:
                member.id = m.id
                print u"updating MP %s %s %s" % (member.name, member.surname, member.uniqueKey)


            member.save()
            count += 1
            if (count >= numberToPrint):
                break;
        print u"succesfully imported / updated %d MPs" % (count)