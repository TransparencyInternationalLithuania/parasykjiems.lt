from django.core.management.base import BaseCommand
from contactdb.management.commands.downloadDocs import GoogleDocUploader
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from contactdb.gdocs import GoogleDocsLogin, GoogleDocsDocument
from settings import *
from cdb_lt_streets.management.commands.ltGeoDataCrawl import RegisterCenterPageLocations, ExtractRange
from pydoc import doc
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):



        """docName = ltGeoDataSources.commonIndexes[0]
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        document = GoogleDocsDocument(login, docName[0])
        document.replaceContents(docName[1])
           """
        #GoogleDocUploader(docName[0], docName[1])

        l = zip(ltGeoDataSources.LithuanianStreetIndexes, RegisterCenterPageLocations.AllData)

        if (len(args) >= 1):
            fromNumber, toNumber = ExtractRange(args[0])
        if (toNumber is None):
            toNumber = len(l)


        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

        for street, regCenterPage in l[fromNumber : toNumber]:
            file = regCenterPage[1]
            if (os.path.exists(file) == False):
                continue
            logger.info("uploading document from file '%s' to location '%s'" % (file, street[0]))
            document = GoogleDocsDocument(login, street[0])
            document.replaceContents(file)