from django.core.management.base import BaseCommand
from django.core import management
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from cdb_lt_streets.tests.TestLTRegisterCenter import LTRegisterCenterHtmlData
from urllib2 import urlopen
from settings import *
from contactdb.gdocs import GoogleDocsLogin, downloadDoc


class Command(BaseCommand):
    args = '<>'
    help = """"""

    def handle(self, *args, **options):

        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

        fromNumber = 0
        toNumber = None
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])
        if toNumber is None:
            toNumber = len(ltGeoDataSources.testIndexes)

        for doc, file in ltGeoDataSources.testIndexes[fromNumber: toNumber]:
            downloadDoc(login, doc, file)

