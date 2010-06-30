from django.core.management.base import BaseCommand
from contactdb.models import *
from django.db import connection, transaction


class Command(BaseCommand):
    args = '<>'
    help = 'Clears all contact db database, and prepares for re-import'



    def handle(self, *args, **options):
        cursor = connection.cursor()

        models = [PollingDistrictStreet, ParliamentMember, Constituency]

        print "Will clear %d models" % (len(models))

        for model in models:
            dbTable = model.objects.model._meta.db_table

            print "Clearing data from %s. (%s)" % (model.objects.model._meta.object_name, dbTable)
            rowCount = model.objects.count()
            print "Total %d rows" % rowCount

            cursor.execute("delete from %s" % (dbTable))
            transaction.commit_unless_managed()

            print "Now it has %d rows" % model.objects.count()

        print "successfully cleared all data. ContactDB empty"

