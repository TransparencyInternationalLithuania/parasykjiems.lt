from django.core.management.base import BaseCommand
from contactdb.imp import LithuanianConstituencyAggregator, ImportSources
from django.db import transaction
import os

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian counties'

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
            print "saved Constituency %s %d" % (c.name, c.nr)
        print "succesfully imported %d constituencies" % (count)