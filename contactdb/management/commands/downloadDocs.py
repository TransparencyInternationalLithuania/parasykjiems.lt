from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient
from settings import *
import csv
from pjutils import uniconsole


import os

class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'


    def openWriter(self, row):
        """ creates a new DictWriter object from row object"""
        fieldNames = [k for k in row.iterkeys()]
        output = "d.csv"
        writer = csv.DictWriter(open(output, "wb"), fieldNames, delimiter = "\t")

        headers = dict( (n,n) for n in fieldNames )
        writer.writerow(headers)

        return writer

    def handle(self, *args, **options):
        allRecords = os.getcwd()

        client = SpreadSheetClient(GOOGLE_DOCS_USER, GOOGLE_DOCS_PASSWORD)
        client.SelectSpreadsheet("ParasykJiems.lt public contact db")
        client.SelectWorksheet(0)


        #writer = csv.writer(open(output, "wb"), csv.excel_tab)

        writer = None
                  #dict([(x, x**2) for x in (2, 4, 6)]) 
        for row in client.GetAllRows():
            # row is a custom object, so lets construct a normal dictionary from it with keys and values
            val = dict([(k, v.text) for k, v in row.iteritems()])
            if (writer is None):
                writer = self.openWriter(val)
            writer.writerow(val)
            print row["surname"].text
            
