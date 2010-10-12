from django.core.management.base import BaseCommand
from contactdb.imp import LithuanianConstituencyAggregator, ImportSources
from django.db import transaction
from pjutils.uniconsole import *
import os

class Command(BaseCommand):
    args = '<>'
    help = """Imports into database all Lithuanian counties. Does not delete any data, only inserts additional.
    Does not update existing data either, as there is no unique-key by which to identify"""

    @transaction.commit_on_success
    def handle(self, *args, **options):
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianConstituencies)
        file = open(allRecords, "r")

        numberToPrint = 9999
        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0
        aggregator = LithuanianConstituencyAggregator(file)
        for c in aggregator.GetDistinctConstituencies():
            c.id = c.nr
            c.save()
            count += 1
            if (count >= numberToPrint):
                break;
            print u"saved Constituency %s %d" % (c.name, c.nr)
        print u"succesfully imported %d constituencies" % (count)