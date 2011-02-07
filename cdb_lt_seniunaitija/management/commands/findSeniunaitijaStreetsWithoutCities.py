#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from django.db import connection, transaction
from pjutils.timemeasurement import TimeMeasurer
import pjutils.uniconsole
import os
from pjutils.exc import ChainnedException
from test.test_iterlen import len
import logging
from contactdb.imp import ImportSources
from cdb_lt_seniunaitija.management.commands.importSeniunaitijaMembers import SeniunaitijaMembersReader
from cdb_lt_seniunaitija.management.commands.importSeniunaitijaStreets import SeniunaitijaAddressExpander, SeniunaitijaAddressExpanderException

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = """Prints all seniunaitija territory streets to stdout. Useful for
checking if there are no errors in data"""

    previousDBRowCount = None

    @transaction.commit_on_success
    def handle(self, *args, **options):
        ImportSources.EsnureExists(ImportSources.LithuanianSeniunaitijaMembers)
        allRecords = os.path.join(os.getcwd(), ImportSources.LithuanianSeniunaitijaMembers)
        reader = SeniunaitijaMembersReader(allRecords)

        fromPrint = 0
        toPrint = 9999999

        if len(args) > 0:
            if (args[0].find(":") > 0):
                split = args[0].split(':')
                fromPrint = int(split[0])
                try:
                    toPrint = int(split[1])
                except:
                    pass
            else:
                toPrint = int(args[0])

        streetExpander = SeniunaitijaAddressExpander()


        imported = 0
        totalNumberOfStreets = 0



        start = TimeMeasurer()

        print "starting to import seniunaitija streets"
        wasError = 0
        count = 0
        for member in reader.ReadMembers():
            if member.territoryStr == "":
                continue
            count += 1
            if fromPrint > member.uniqueKey:
                continue
            if toPrint < member.uniqueKey:
                break
            numberOfStreets = 0


            try:
                for street in streetExpander.ExpandStreet(member.territoryStr):
                    #print "street \t %s \t %s \t %s \t %s" % (street.city, street.street, street.numberFrom, street.numberTo)
                    if street.city is None:
                        print "territory for: %s %s" % (member.uniqueKey, member.seniunaitijaStr)
                        print "street \t %s \t %s \t %s \t %s" % (street.city, street.street, street.numberFrom, street.numberTo)
                        numberOfStreets += 1
                        break
            except SeniunaitijaAddressExpanderException as e:
                logger.error("""Error in seniunaitija teritory nr '%s'
ErrorDetails = %s""" % (member.uniqueKey, e.message))
                wasError = wasError + 1
                continue

            imported += 1
            totalNumberOfStreets += numberOfStreets
            seconds = start.ElapsedSeconds()
            if seconds == 0:
                rate = "unknown"
            else:
                rate = str(totalNumberOfStreets / seconds)

        if wasError == 0:
            print "succesfully imported %d seniunaitija territories, total %d streets" % (imported, totalNumberOfStreets)
        else:
            print "Errors. Imported only part of the seniunaitija territories"
            print "Imported %d seniunaitija territories, total %d streets" % (imported, totalNumberOfStreets)
            print "There was %s errors" % (wasError)
        print "total spent time %d seconds" % (start.ElapsedSeconds())
