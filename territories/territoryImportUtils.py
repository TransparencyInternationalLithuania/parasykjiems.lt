import csv
import os
from contactdb.importUtils import readRow, getInstitutionNameFromColumn
from django.db import transaction, connection
from contactdb.models import Institution
from pjutils.exc import ChainedException
from territories.ltPrefixes import allStreetEndings, changeStreetFromShortToLongForm
from territories.models import CountryAddresses, InstitutionTerritory
import logging
logger = logging.getLogger(__name__)

class InstitutionNotFound(ChainedException):
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


class InstitutionCache(object):
    def __init__(self):
        self.institutionCache = None

    def initCache(self):
        self.institutionCache = {}
        for i in Institution.objects.all():
            key = self.getKey(i.name, i.institutionType.code)
            self.institutionCache[key] = i

    def getKey(self, name, institutionCode):
        return "%s %s" % (name, institutionCode)

    def getInstitution(self, name, institutionCode):
        if self.institutionCache is None:
            self.initCache()
        key = self.getKey(name, institutionCode)
        if self.institutionCache.has_key(key):
            return self.institutionCache[key]
        raise InstitutionNotFound(message="Institution with name '%s' was not found. Perhaps it was not imported when members were created" % name)



class InstitutionStreetCache:
    def __init__(self):
        self.streetCache = {}
        self.initializeCache()

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
        cursor.execute(sql)
        lst = cursor.fetchall()
        transaction.commit_unless_managed()
        if len(lst) == 0:
            return
        if len(lst) != len(all):
            raise ChainedException(message="cache not correctly initialized")


        for i in range(0, len(lst)):
            obj = all[i]
            keyTuple = lst[i]
            institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd = keyTuple
            if numberOdd is not None:
                numberOdd = bool(numberOdd)
            key = self.getCacheKey(institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
            self.streetCache[key] = obj



    def isStreetInCache(self, institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd):
        key = self.getCacheKey(institutionCode, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
        return self.streetCache.has_key(key)





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

        street = changeStreetFromShortToLongForm(street)

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

    def __init__(self, institutionCode, institutionStreetCache = None, institutionCache = None, printDetailedInfo = False):
        self.missingInstitutions = {}
        self.printDetailedInfo = printDetailedInfo
        self.unparsedInstitutionTerritories = {}
        self.institutionCode = institutionCode

        self.institutionCache = institutionCache
        if self.institutionCache is None:
            self.institutionCache = InstitutionCache()
        self.importer = institutionStreetCache
        if institutionStreetCache is None:
            self.importer = InstitutionStreetCache()

    @transaction.commit_on_success
    def importInstitutionTerritoryYielder(self, addressYielder):
        logger.info(u"Import street index data ")

        processed = 0
        rowNumber = 0
        for territoryAddress in addressYielder.yieldTerritories():
            rowNumber += 1
            institutionKey = territoryAddress['institutionKey']
            municipality = territoryAddress['municipality']
            civilParish = territoryAddress['civilParish']
            city = territoryAddress['city']
            street = territoryAddress['street']
            numberFrom = territoryAddress['numberFrom']
            numberTo = territoryAddress['numberTo']
            numberOdd = territoryAddress['numberOdd']
            comment = u""
            if territoryAddress.has_key("comment"):
                comment = territoryAddress['comment']
                if comment is None:
                    comment = u""

            processed += 1

            if self.printDetailedInfo:
                moreInfo = u""
                if hasattr(addressYielder, "currentTerritoryInfo"):
                    moreInfo = addressYielder.currentTerritoryInfo()
                print "%s, %s, %s, %s, %s, %s, %s, %s, %s '%s'. More info: '%s'. Yielder: '%s'" % (institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd, rowNumber, institutionKey, moreInfo, addressYielder)
            try:
                institution = self.institutionCache.getInstitution(institutionKey, institutionCode = self.institutionCode)
            except InstitutionNotFound:
                moreInfo = u""

                if hasattr(addressYielder, "currentTerritoryInfo"):
                    moreInfo = addressYielder.currentTerritoryInfo()

                self.missingInstitutions[institutionKey]=u"%s '%s'. More info: '%s'. Yielder: '%s'" % (rowNumber, institutionKey, moreInfo, addressYielder)
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
                newObject.comment = comment
                try:
                    newObject.save()
                except Exception as e:
                    moreInfo = u""
                    if hasattr(addressYielder, "currentTerritoryInfo"):
                        moreInfo = addressYielder.currentTerritoryInfo()
                    self.unparsedInstitutionTerritories[institutionKey]=u"%s '%s'. More info: '%s'. Yielder: '%s', exception : 'e'" % (rowNumber, institutionKey, moreInfo, addressYielder, e)
                    continue

                self.importer.addToCache(newObject)

            if processed % 400 == 0:
                logger.info("Imported %s addresses" % processed)
        logger.info("Imported %s addresses" % processed)

        self.unparsedInstitutionTerritories = dict(self.unparsedInstitutionTerritories, **addressYielder.unparsedInstitutions)

def importInstitutionTerritoryYielder(addressYielder, institutionCode, printDetailedInfo = False, institutionCache = None, institutionStreetCache = None):
    """ imports institution addresses.
    addressYielder is a class with method yieldTerritories, which yields tuples in this form:
    (institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
    """

    importer = InstitutionStreetImporter(institutionCode = institutionCode, printDetailedInfo = printDetailedInfo, institutionCache = institutionCache, institutionStreetCache = institutionStreetCache)
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
