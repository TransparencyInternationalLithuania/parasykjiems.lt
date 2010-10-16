from django.core.management.base import BaseCommand
from contactdb.models import *
from django.db import connection, transaction
from cdb_lt_mps.models import PollingDistrictStreet, ParliamentMember, Constituency
from cdb_lt_civilparish.models import CivilParishMember
from cdb_lt_streets.models import HierarchicalGeoData
from cdb_lt_seniunaitija.models import SeniunaitijaMember
from cdb_lt_municipality.models import MunicipalityMember

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
        cursor = connection.cursor()

        models = [PollingDistrictStreet,
                  ParliamentMember,
                  Constituency,
                  CivilParishMember,
                  HierarchicalGeoData,
                  MunicipalityMember,
                  SeniunaitijaMember]

        ClearTablesData(models)
        
        print "successfully cleared all data. ContactDB empty"

