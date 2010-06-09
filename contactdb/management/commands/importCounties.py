from django.core.management.base import BaseCommand
from contactdb.imp import LithuanianCountyAggregator, ImportSources
import os

class Command(BaseCommand):
    args = '<>'
    help = 'Imports into database all Lithuanian counties'

    def handle(self, *args, **options):
        allRecords = os.getcwd() + ImportSources.LithuanianCounties
        file = open(allRecords, "r")

        numberToPrint = 9999
        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0
        aggregator = LithuanianCountyAggregator(file)
        for c in aggregator.GetDistinctCounties():
            c.id = c.nr
            c.save()
            count += 1
            if (count >= numberToPrint):
                break;
            print "saved County %s %d" % (c.name, c.nr)
        print "succesfully imported %d counties" % (count)