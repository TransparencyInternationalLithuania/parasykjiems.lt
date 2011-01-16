from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient, GoogleDocsLogin
from settings import *
import csv
import pjutils.uniconsole
from contactdb.imp import GoogleDocsSources, ImportSources
import os
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
import gdata
from pjutils.deprecated import deprecated
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange

logger = logging.getLogger(__name__)

class GoogleDocDownloader:
    """ Downloads a google doc, and saves it to a file as csv file.
    This class is using an old way to connect to google docs and download a doc. This takes much longer,
    but we can control the way the file is saved to disk.

    You can use some of the helper methods defined in the same package instead of using this class directly"""

    def __init__(self):
        self.client = SpreadSheetClient(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

    def _openWriter(self, fileName, row):
        """ creates a new DictWriter object from row object. Writes header row"""
        fieldNames = [k for k in row.iterkeys()]

        writer = csv.DictWriter(open(fileName, "wb"), fieldNames, delimiter = ImportSources.Delimiter)

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
                writer = self._openWriter(fileName, val)
            writer.writerow(val)
        print "ok"

        self.client.GetAllRows()





def downloadDoc(login, docName, fileName):
    """ Uses GoogleDocDownloader inside to actually download a google doc and save it to file
    as csv"""
    #document = GoogleDocsDocument(login, docName)
    #document.downloadDocument(fileName)
    dir_util.mkpath(os.path.dirname(fileName))
    GoogleDocDownloader().downloadDoc(docName, fileName)




class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'

    def handle(self, *args, **options):
        """ Downloads documents as csv (tab-delimited) files from google docs"""

        fromNumber = 0
        toNumber = None

        allDocs = [(GoogleDocsSources.LithuanianMPs, ImportSources.LithuanianMPs),
                (GoogleDocsSources.LithuanianCivilParishMembers, ImportSources.LithuanianCivilParishMembers),
                (GoogleDocsSources.LithuanianMunicipalityMembers, ImportSources.LithuanianMunicipalityMembers),
                (GoogleDocsSources.LithuanianSeniunaitijaMembers, ImportSources.LithuanianSeniunaitijaMembers),
                (GoogleDocsSources.LithuanianMunicipalities, ImportSources.LithuanianMunicipalities),
                (GoogleDocsSources.LithuanianCivilParishes, ImportSources.LithuanianCivilParishes)

        ]
        if (len(args) >= 1):
            fromNumber, toNumber = ExtractRange(args[0])
        if (toNumber is None):
            toNumber = len(allDocs)

        elapsedTime = TimeMeasurer()
        print "Will download docs from %s to %s " % (fromNumber, toNumber)
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        for docSource, importSource in allDocs[fromNumber:toNumber]:
            downloadDoc(login, docSource, importSource)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()