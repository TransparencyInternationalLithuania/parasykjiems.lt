from django.core.management.base import BaseCommand
from contactdb.models import *
from django.db import connection, transaction
from contactdb.management.commands.clearcontactDB import ClearTablesData


class Command(BaseCommand):
    args = '<>'
    help = 'Clears all ltGeoData db database, and prepares for re-import'


    def handle(self, *args, **options):
        models = [HierarchicalGeoData]


        ClearTablesData(models)
        print "successfully cleared all data. ContactDB empty"

