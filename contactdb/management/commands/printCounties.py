from django.core.management.base import BaseCommand, CommandError
from contactdb.imp import ImportSources, LithuanianCountyReader, LithuanianCountyAggregator
import os

class Command(BaseCommand):
    args = '<numberOfCountiesToPrint>'
    help = 'Prints number of Lithuanian counties'

    def handle(self, *args, **options):
        allRecords = os.getcwd() + ImportSources.LithuanianCounties
        file = open(allRecords, "r")

        numberToPrint = 999999;
        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0
        aggregator = LithuanianCountyAggregator(file)
        for county in aggregator.GetDistinctCounties():
            print "\n"
            print "County: " + county
            count += 1
            if (count >= numberToPrint):
                break