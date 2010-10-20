from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient
from settings import *
import csv
import pjutils.uniconsole
from contactdb.imp import GoogleDocsSources, ImportSources
import os


""" Downloads a google doc, and saves it to a file as csv file.
You can use some of the helper methods defined in the same package instead of using this class directly"""
class GoogleDocDownloader:
    def __init__(self):
        self.client = SpreadSheetClient(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

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
            d[k] = d[k].replace("\n", " ")

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



""" Uses GoogleDocDownloader inside to actually download a google doc and save it to file
as csv"""
def downloadDoc(docName, fileName):
    GoogleDocDownloader().downloadDoc(docName, fileName)

class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'




    def handle(self, *args, **options):
        """ Downloads documents as csv (tab-delimited) files from google docs"""
        allRecords = os.getcwd()

        downloadDoc(GoogleDocsSources.LithuanianMPs, ImportSources.LithuanianMPs)
        downloadDoc(GoogleDocsSources.LithuanianCivilParishMembers, ImportSources.LithuanianCivilParishMembers)
        downloadDoc(GoogleDocsSources.LithuanianMunicipalityMembers, ImportSources.LithuanianMunicipalityMembers)
        downloadDoc(GoogleDocsSources.LithuanianSeniunaitijaMembers, ImportSources.LithuanianSeniunaitijaMembers)
        downloadDoc(GoogleDocsSources.LithuanianMunicipalities, ImportSources.LithuanianMunicipalities)
        downloadDoc(GoogleDocsSources.LithuanianCivilParishes, ImportSources.LithuanianCivilParishes)


            
