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