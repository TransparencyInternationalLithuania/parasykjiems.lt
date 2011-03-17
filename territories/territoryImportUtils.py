import csv
import os
from contactdb.importUtils import readRow, getInstitutionNameFromColumn
from django.db import transaction, connection
from pjutils import uniconsole
from contactdb.models import Institution
from pjutils.exc import ChainnedException
from territories.models import CountryAddresses, InstitutionTerritory
import logging
logger = logging.getLogger(__name__)

class InstitutionNotFound(ChainnedException):
    pass

class CountryStreetCache:
    def __init__(self):
        self.streetCache = {}
        self.initializeCache()
        pass

    def getCacheKey(self, municipality, civilparish, city, street):
        return "%s %s %s %s" % (municipality, civilparish, city, street)

    def addToCache(self, record):
        key = self.getCacheKey(record.municipality, record.civilParish, record.city, record.street)
        self.streetCache[key] = record

    def initializeCache(self):
        for r in CountryAddresses.objects.all():
            self.addToCache(r)

    def isInCache(self, municipality, civilparish, city, street):
        key = self.getCacheKey(municipality, civilparish, city, street)
        return self.streetCache.has_key(key)


class InstitutionStreetCash:
    def __init__(self, institutionCode):
        self.streetCache = {}
        self.initializeCache()

        self.institutionCode = institutionCode
        self.institutionCache = {}

    def getCacheKey(self, institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd):
        return "%s %s %s %s %s %s %s %s" % (institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)

    def addToCache(self, record):
        key = self.getCacheKey(record.institution.institutionType.code, record.municipality, record.civilParish, record.city, record.street, record.numberFrom, record.numberTo, record.numberOdd)
        self.streetCache[key] = record

    def initializeCache(self):
        all = list(InstitutionTerritory.objects.all())


        sql = """select code, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd from territories_institutionterritory it
left join contactdb_institution i on i.id = it.institution_id
left join contactdb_institutiontype itype on itype.id = i.institutionType_id"""

        cursor = connection.cursor()
        lst = list(cursor.execute(sql))
        transaction.commit_unless_managed()

        for i in range(0, len(all)):
            obj = all[i]
            keyTuple = lst[i]
            institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd = keyTuple
            if numberOdd != None:
                numberOdd = bool(numberOdd)
            key = self.getCacheKey(institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
            self.streetCache[key] = obj



    def isStreetInCache(self, institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd):
        key = self.getCacheKey(institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
        return self.streetCache.has_key(key)

    def getInstitution(self, name):
        if self.institutionCache.has_key(name):
            return self.institutionCache[name]

        try:
            i = Institution.objects.all().filter(name = name).filter(institutionType__code=self.institutionCode).get()
            self.institutionCache[name] = i
            return i
        except Institution.DoesNotExist:
            raise InstitutionNotFound(message="Institution with name '%s' was not found. Perhaps it was not imported when members were created" % name)





def importCountryFile(fileName, delimiter=",", streetCache = None):
    print u"Import street index data from csv file %s" % fileName

    dictReader = csv.DictReader(open(fileName, "rt"), delimiter = delimiter)
    if streetCache is None:
        streetCache = CountryStreetCache()

    processed = 0
    for row in dictReader:
        id = readRow(row, "id", default=u"")
        municipality = readRow(row, "municipality", default=u"")
        civilParish = readRow(row, "civilparish", default=u"")
        city = readRow(row, "city", default=u"")
        city_genitive = readRow(row, "City_genitive")
        street = readRow(row, "street", default=u"")

        if city.strip() == u"":
            continue

        processed += 1
        if not streetCache.isInCache(municipality, civilParish, city, street):
            newObject = CountryAddresses()
            newObject.street = street
            newObject.municipality = municipality
            newObject.city = city
            newObject.city_genitive = city_genitive
            newObject.civilParish = civilParish
            newObject.save()
            streetCache.addToCache(newObject)

        if processed % 200 == 0:
            logger.info("Imported %s addresses" % processed)

def cityNameGetterStandard(csvRow):
    return readRow(csvRow, "city")

class InstitutionStreetImporter(object):

    def __init__(self, institutionCode):
        self.missingInstitutions = {}
        self.unparsedInstitutionTerritories = {}
        self.importer = InstitutionStreetCash(institutionCode = institutionCode)

    @transaction.commit_on_success
    def importInstitutionTerritoryYielder(self, addressYielder):
        logger.info(u"Import street index data ")

        processed = 0
        rowNumber = 0
        for tuple in addressYielder.yieldTerritories():
            rowNumber += 1
            institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd = tuple

            processed += 1

            try:
                institution = self.importer.getInstitution(institutionKey)
            except InstitutionNotFound:
                self.missingInstitutions[institutionKey]=u"%s %s" % (rowNumber, institutionKey)
                continue
            institutionCode = institution.institutionType.code

            if numberFrom != None:
                pass
            if not self.importer.isStreetInCache(institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd):
                newObject = InstitutionTerritory()
                newObject.institution = institution

                newObject.municipality = municipality
                newObject.civilParish = civilParish
                newObject.city = city
                newObject.street = street
                newObject.numberFrom = numberFrom
                newObject.numberTo = numberTo
                newObject.numberOdd = numberOdd
                newObject.save()
                self.importer.addToCache(newObject)

            if processed % 400 == 0:
                logger.info("Imported %s addresses" % processed)
        logger.info("Imported %s addresses" % processed)

        self.unparsedInstitutionTerritories = dict(self.unparsedInstitutionTerritories, **addressYielder.unparsedInstitutions)

def importInstitutionTerritoryYielder(addressYielder, institutionCode):
    """ imports institution addresses.
    addressYielder is a class with method yieldTerritories, which yields tuples in this form:
    (institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
    """

    importer = InstitutionStreetImporter(institutionCode = institutionCode)
    importer.importInstitutionTerritoryYielder(addressYielder = addressYielder)

    for institutionName, errorMessage in importer.missingInstitutions.iteritems():
        print "missing institution %s: %s" % (institutionName, errorMessage)


    for institutionName, errorMessage in importer.unparsedInstitutionTerritories.iteritems():
        print "could not parse territory %s: %s" % (institutionName, errorMessage)


@transaction.commit_on_success
def importCountryData(csvFileNames):
    streetCache = CountryStreetCache()
    for f in csvFileNames:
        f = os.path.join(os.getcwd(), f)
        importCountryFile(fileName=f, streetCache=streetCache)