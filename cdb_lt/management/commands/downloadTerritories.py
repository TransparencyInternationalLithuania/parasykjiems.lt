from django.core.management.base import BaseCommand
from cdb_lt.management.commands.importSources import ltGeoDataSources_Country
from pjutils.args.Args import ExtractRange
from pjutils.gdocsUtils import GoogleDocsLogin, downloadDoc
from settings import *

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
            toNumber = len(ltGeoDataSources_Country.LithuanianAddresses)

        for doc, file in ltGeoDataSources_Country.LithuanianAddresses[fromNumber: toNumber]:
            downloadDoc(login, doc, file)