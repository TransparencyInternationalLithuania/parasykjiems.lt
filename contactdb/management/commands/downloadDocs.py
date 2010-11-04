from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient, SpreadSheetUpdater
from settings import *
import csv
import pjutils.uniconsole
from contactdb.imp import GoogleDocsSources, ImportSources
import os
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
logger = logging.getLogger(__name__)

class SpreadSheetDiffUploader:

    def __init__(self, docName, fileName):
        logger.debug("logging in to GDocs")
        self.client = SpreadSheetClient(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        self.client.SelectSpreadsheet(docName)
        self.client.SelectWorksheet(0)
        logger.debug("logged into GDocs")

        logger.debug("reading all csv file")
        self.dictReader = csv.DictReader(open(fileName, "rt"), delimiter = "\t")
        self.dictReader = list(self.dictReader)
        logger.debug("read all csv file")

        self.UploadDocument()

    def dictionariesEqual(self, dict1, dict2):
        for key1 in dict1.iterkeys():
            val1 = dict1[key1]
            if (dict2.has_key(key1) == False):
                if val1 is None:
                    continue
                if val1.strip() == u"":
                    continue
            val2 = dict2[key1]
            if (val1 is None):
                val1 = ""
            val1 = val1.strip()

            if (val2 is None):
                val2 = ""
            val2 = val2.strip()
            if (val1 != val2):
                return False
        return True



    def UploadDocument(self):
        logger.debug("preparing to update document")
        csvCount = len(self.dictReader)
        gdocRows = [self.client.ToDictionaryFromRow(r) for r in self.client.GetAllRows()]
        gdocCount = len(gdocRows)

        logger.debug("pre-fetched all rows")
        updater = SpreadSheetUpdater(self.client)

        maxx = max(csvCount, gdocCount)
        i = - 1
        logger.debug("starting to update")
        for gdocValues in gdocRows:
            i += 1
            csvValues = self.dictReader[i]

            if (self.dictionariesEqual(gdocValues, csvValues) == True):
                logger.debug("Not changed %s / %s" % (i, maxx))
                continue

            logger.debug("Uploading row %s / %s" % (i, maxx))
            updater.UpdateRow(i, self.dictReader[i])

        for i in range(i, maxx):
            logger.debug("Uploading row %s / %s" % (i, maxx))
            if i >= csvCount:
                updater.DeleteRow(i)
            elif i >= gdocCount:
                updater.AppendRow(self.dictReader[i])
            else:
                updater.UpdateRow(i, self.dictReader[i])









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
            val = self.client.ToDictionaryFromRow(row)
            if (writer is None):
                writer = self.openWriter(fileName, val)
            writer.writerow(val)
        print "ok"

        self.client.GetAllRows()





def downloadDoc(docName, fileName):
    """ Uses GoogleDocDownloader inside to actually download a google doc and save it to file
    as csv"""
    GoogleDocDownloader().downloadDoc(docName, fileName)




class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'




    def handle(self, *args, **options):
        """ Downloads documents as csv (tab-delimited) files from google docs"""
        allRecords = os.getcwd()





        docName = ltGeoDataSources.commonIndexes[0]
        SpreadSheetDiffUploader(docName[0], docName[1])

        """
        downloadDoc(GoogleDocsSources.LithuanianMPs, ImportSources.LithuanianMPs)
        downloadDoc(GoogleDocsSources.LithuanianMPs, ImportSources.LithuanianMPs)
        downloadDoc(GoogleDocsSources.LithuanianCivilParishMembers, ImportSources.LithuanianCivilParishMembers)
        downloadDoc(GoogleDocsSources.LithuanianMunicipalityMembers, ImportSources.LithuanianMunicipalityMembers)
        downloadDoc(GoogleDocsSources.LithuanianSeniunaitijaMembers, ImportSources.LithuanianSeniunaitijaMembers)
        downloadDoc(GoogleDocsSources.LithuanianMunicipalities, ImportSources.LithuanianMunicipalities)
        downloadDoc(GoogleDocsSources.LithuanianCivilParishes, ImportSources.LithuanianCivilParishes)


        """
