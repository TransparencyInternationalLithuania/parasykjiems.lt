from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient
from settings import *

from pjutils import uniconsole


import os

class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'

    @transaction.commit_on_success
    def handle(self, *args, **options):
        allRecords = os.getcwd()

        client = SpreadSheetClient(GOOGLE_DOCS_USER, GOOGLE_DOCS_PASSWORD)
        client.SelectSpreadsheet("ParasykJiems.lt public contact db")
        client.SelectWorksheet(0)
        for row in client.GetAllRows():
            print row["surname"].text
            
