import csv
import os
from contactdb.importUtils import readRow
import logging
from territories.ltPrefixes import changeStreetFromShortToLongForm

logger = logging.getLogger(__name__)


class civilParishStreetReader(object):
    def __init__(self, csvFileNames, institutionNameGetter, cityNameGetter, delimiter=","):

        self.csvFileNames = csvFileNames
        self.delimiter = delimiter
        self.cityNameGetter = cityNameGetter
        self.institutionNameGetter = institutionNameGetter
        self.unparsedInstitutions = {}

    def currentTerritoryInfo(self):
        return "rowNumber  '%s' file'%s'" % (self.rowNumber, self.fileName)

    def yieldFromFile(self, fileName):
        logger.info(u"Import street index data from csv file %s" % fileName)

        dictReader = csv.DictReader(open(fileName, "rt"), delimiter = self.delimiter)

        self.fileName = fileName
        processed = 0
        self.rowNumber = 0
        numberFrom = u""
        numberTo = u""
        numberOdd = None
        
        for row in dictReader:
            self.rowNumber += 1
            municipality = readRow(row, "municipality")
            civilParish = readRow(row, "civilparish")
            city = self.cityNameGetter(row)
            street = readRow(row, "street")
            street = changeStreetFromShortToLongForm(street)
            institutionKey = self.institutionNameGetter(row)
            if city.strip() == u"":
               continue
            yield {"institutionKey" : institutionKey, "municipality" : municipality,
                           "civilParish" : civilParish, "city": city,
                           "street" : street, "numberFrom" : numberFrom,
                           "numberTo" : numberTo, "numberOdd": numberOdd}





    def yieldTerritories(self):
        for f in self.csvFileNames:
            f = os.path.join(os.getcwd(), f)
            for t in self.yieldFromFile(f):
                yield t

