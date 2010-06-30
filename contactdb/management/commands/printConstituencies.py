from django.core.management.base import BaseCommand, CommandError
from contactdb.imp import ImportSources, LithuanianConstituencyReader, LithuanianConstituencyAggregator
import os

class Command(BaseCommand):
    args = '<numberOfCountiesToPrint>'
    help = 'Prints Lithuanian counties. Pass a number to print only the first x counties'

    def handle(self, *args, **options):
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianConstituencies)
        file = open(allRecords, "r")

        numberToPrint = 999999
        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0
        aggregator = LithuanianConstituencyAggregator(file)
        for constituency in aggregator.GetDistinctConstituencies():
            print "\n"
            print "Constituency: " + constituency.ToString()
            count += 1
            if (count >= numberToPrint):
                break