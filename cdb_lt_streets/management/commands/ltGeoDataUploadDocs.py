from django.core.management.base import BaseCommand
from contactdb.management.commands.downloadDocs import GoogleDocUploader
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
from contactdb.gdocs import GoogleDocsLogin, GoogleDocsDocument
from settings import *


class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):



        docName = ltGeoDataSources.commonIndexes[0]
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        document = GoogleDocsDocument(login, docName[0])
        document.replaceContents(docName[1])

        #GoogleDocUploader(docName[0], docName[1])

        #for doc, file in ltGeoDataSources.LithuanianStreetIndexes:
         #   uploadDoc(doc, file)