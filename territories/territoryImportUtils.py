import csv
import os
from contactdb.importUtils import readRow
from django.db import transaction
from territories.models import CountryAddresses
import logging
logger = logging.getLogger(__name__)

class CountryStreetImporter:
    def __init__(self):
        self.streetCache = {}
        self.initializeCache()
        pass

    def getCacheKey(self, municipality, civilparish, city, street):
        return "%s %s %s %s" % (municipality, civilparish, city, street)

    def addToCache(self, record):
        self.streetCache[self.getCacheKey(record.municipality, record.civilparish, record.city, record.street)] = record

    def initializeCache(self):
        for r in CountryAddresses.objects.all():
            self.addToCache(r)

    def isInCache(self, municipality, civilparish, city, street):
        key = self.getCacheKey(municipality, civilparish, city, street)
        return self.streetCache.has_key(key)

@transaction.commit_on_success
def importFile(fileName, delimiter=","):
    print u"Import street index data from csv file %s" % fileName

    dictReader = csv.DictReader(open(fileName, "rt"), delimiter = delimiter)
    importer = CountryStreetImporter()

    processed = 0
    for row in dictReader:
        id = readRow(row, "id", default=u"")
        #country = readRow(row, "country", default=u"")
        #county = readRow(row, "county", default=u"")
        municipality = readRow(row, "municipality", default=u"")
        civilParish = readRow(row, "civilparish", default=u"")
        city = readRow(row, "city", default=u"")
        city_genitive = readRow(row, "City_genitive")
        street = readRow(row, "street", default=u"")

        if city.strip() == u"":
            continue

        processed += 1
        if not importer.isInCache(municipality, civilParish, city, street):
            newObject = CountryAddresses()
            newObject.street = street
            newObject.municipality = municipality
            newObject.city = city
            newObject.city_genitive = city_genitive
            newObject.civilParish = civilParish
            newObject.save()
            importer.addToCache(newObject)

        if processed % 200 == 0:
            logger.info("Imported %s addresses" % processed)



def importCountryData(csvFileNames):
    for f in csvFileNames:
        f = os.path.join(os.getcwd(), f)
        importFile(fileName=f)