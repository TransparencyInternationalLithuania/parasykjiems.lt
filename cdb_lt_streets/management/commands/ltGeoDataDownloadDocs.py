from django.core.management.base import BaseCommand
from contactdb.management.commands.downloadDocs import downloadDoc
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from contactdb.gdocs import GoogleDocsLogin
from settings import *


class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        for doc, file in ltGeoDataSources.LithuanianStreetIndexes:
            downloadDoc(login, doc, file)