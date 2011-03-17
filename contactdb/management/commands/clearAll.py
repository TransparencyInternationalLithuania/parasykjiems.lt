from django.core.management.base import BaseCommand
from django.db import connection, transaction

def ClearTablesData(listOfDjangoModels):
    print "Will clear %d models" % (len(listOfDjangoModels))
    cursor = connection.cursor()
    for model in listOfDjangoModels:
        dbTable = model.objects.model._meta.db_table

        print "Clearing data from %s. (%s)" % (model.objects.model._meta.object_name, dbTable)
        rowCount = model.objects.count()
        print "Total %d rows" % rowCount

        cursor.execute("delete from %s" % (dbTable))
        transaction.commit_unless_managed()

        print "Now it has %d rows" % model.objects.count()

class Command(BaseCommand):
    args = '<>'
    help = 'Clears all contact db database, and prepares for re-import'



    def handle(self, *args, **options):

        #ClearTablesData(models)
        
        #print "successfully cleared all data. ContactDB empty"
        print "dummy function, will be removed"

