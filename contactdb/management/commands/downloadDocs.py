from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient
from settings import *
import csv
import pjutils.uniconsole
from contactdb.imp import GoogleDocsSources, ImportSources



import os

class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'


    def openWriter(self, fileName, row):
        """ creates a new DictWriter object from row object. Writes header row"""
        fieldNames = [k for k in row.iterkeys()]
        
        writer = csv.DictWriter(open(fileName, "wb"), fieldNames, delimiter = "\t")

        headers = dict( (n,n) for n in fieldNames )
        writer.writerow(headers)

        return writer

    def buildValuesDict(self, googleRow):
        """ builds a dictionary, and encodes values with utf-8"""
        d = dict([(k, v.text) for k, v in googleRow.iteritems()])

        for k in d.iterkeys():
            if d[k] is None:
                continue

            d[k] = d[k].encode("utf-8")
        return d



    def downloadDoc(self, docName, fileName):
        #client.SelectSpreadsheet("ParasykJiems.lt public contact db")
        print "downloading  '%s' to '%s'" % (docName, fileName)
        self.client.SelectSpreadsheet(docName)
        self.client.SelectWorksheet(0)


        #writer = csv.writer(open(output, "wb"), csv.excel_tab)
        fileName = os.path.join(os.getcwd(), fileName) 

        writer = None
        for row in self.client.GetAllRows():
            # row is a custom object, so lets construct a normal dictionary from it with keys and values
            val = self.buildValuesDict(row)
            if (writer is None):
                writer = self.openWriter(fileName, val)
            writer.writerow(val)
        print "ok"


    def handle(self, *args, **options):
        """ Downloads documents as csv (tab-delimited) files from google docs"""
        allRecords = os.getcwd()

        self.client = SpreadSheetClient(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

        self.downloadDoc(GoogleDocsSources.LithuanianMPs, ImportSources.LithuanianMPs)


            
