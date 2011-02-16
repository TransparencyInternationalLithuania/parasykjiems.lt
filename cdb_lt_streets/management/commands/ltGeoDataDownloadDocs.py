from django.core.management.base import BaseCommand
from contactdb.management.commands.downloadDocs import downloadDoc
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from contactdb.gdocs import GoogleDocsLogin
from settings import *
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange


class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

        fromNumber = 0
        toNumber = None
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])
        if toNumber is None:
            toNumber = len(ltGeoDataSources.LithuanianStreetIndexes)

        for doc, file in ltGeoDataSources.LithuanianStreetIndexes[fromNumber: toNumber]:
            downloadDoc(login, doc, file)