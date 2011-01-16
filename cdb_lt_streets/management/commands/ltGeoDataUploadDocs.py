from django.core.management.base import BaseCommand
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from contactdb.gdocs import GoogleDocsLogin, GoogleDocsUploader
from settings import *
from cdb_lt_streets.management.commands.ltGeoDataCrawl import RegisterCenterPageLocations, ExtractRange
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        l = zip(ltGeoDataSources.LithuanianStreetIndexes, RegisterCenterPageLocations.AllData)

        fromNumber = 0
        toNumber = None
        if (len(args) >= 1):
            fromNumber, toNumber = ExtractRange(args[0])
        if (toNumber is None):
            toNumber = len(l)


        print "Following docs will be upload:"
        num = 0
        for street, regCenterPage in l[fromNumber : toNumber]:
            file = regCenterPage[1]
            logger.info("%s '%s' to location '%s'" % (num, file, street[0]))
            num += 1

        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

        for street, regCenterPage in l[fromNumber : toNumber]:
            file = regCenterPage[1]
            if (os.path.exists(file) == False):
                continue
            logger.info("uploading document from file '%s' to location '%s'" % (file, street[0]))
            document = GoogleDocsUploader(login, street[0])
            document.replaceContents(file)