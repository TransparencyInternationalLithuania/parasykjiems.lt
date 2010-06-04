from django.core.management.base import BaseCommand, CommandError
from contactdb.imp import getLocations
import os

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        allRecords = os.getcwd() + "/contactdb/sources/apygardos.txt"
        file = open(allRecords, "r")


        if len(args) > 0:
            numberToPrint = int(args[0])

        count = 0
        for loc in getLocations(file):
            print "\n"
            print "District : " + loc.District + " \n County: " + loc.County + "\n ElectionDistrict " + loc.ElectionDistrict
            count += 1
            if (count == numberToPrint):
                break;