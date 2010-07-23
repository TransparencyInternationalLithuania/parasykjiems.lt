from django.core.management.base import BaseCommand
from contactdb.models import *
from django.db import connection, transaction
from contactdb.management.commands.ltGeoDataDBClear import ClearTablesData


class Command(BaseCommand):
    args = '<>'
    help = 'Clears all contact db database, and prepares for re-import'



    def handle(self, *args, **options):
        cursor = connection.cursor()

        models = [PollingDistrictStreet, ParliamentMember, Constituency]

        ClearTablesData(models)
        
        print "successfully cleared all data. ContactDB empty"

