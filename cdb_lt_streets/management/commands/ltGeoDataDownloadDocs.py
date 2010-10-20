from django.core.management.base import BaseCommand
from contactdb.management.commands.downloadDocs import downloadDoc
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources


class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):
        for doc, file in ltGeoDataSources.LithuanianStreetIndexes:
            downloadDoc(doc, file)