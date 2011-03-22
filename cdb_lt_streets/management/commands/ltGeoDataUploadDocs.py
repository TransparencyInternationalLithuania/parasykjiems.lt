from django.core.management.base import BaseCommand
from cdb_lt.management.commands.importSources import ltGeoDataSources_Country
from cdb_lt_streets.management.commands.ltGeoDataCrawl import RegisterCenterPageLocations
from settings import *
import time
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        l = zip(ltGeoDataSources_Country.LithuanianAddresses, RegisterCenterPageLocations.AllData)

        fromNumber = 0
        toNumber = None
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])
        if toNumber is None:
            toNumber = len(l)


        print "Following docs will be upload:"
        num = 0
        for street, regCenterPage in l[fromNumber : toNumber]:
            file = regCenterPage[1]
            logger.info("%s '%s' to location '%s'" % (num, file, street[0]))
            num += 1

        print "Is this info ok? Will sleep for 5 seconds"
        time.sleep(5)

        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

        for street, regCenterPage in l[fromNumber : toNumber]:
            file = regCenterPage[1]
            file = os.path.join(os.getcwd(), file)
            if not os.path.exists(file):
                print "file '%s' does not exist, skip" % file
                continue
            logger.info("uploading document from file '%s' to location '%s'" % (file, street[0]))
            document = GoogleDocsUploader(login, street[0])
            document.replaceContents(file)