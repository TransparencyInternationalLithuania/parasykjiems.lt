import csv
import os
from contactdb.importUtils import readRow
import logging
logger = logging.getLogger(__name__)


class civilParishStreetReader(object):
    def __init__(self, csvFileNames, institutionNameGetter, cityNameGetter, delimiter=","):

        self.csvFileNames = csvFileNames
        self.delimiter = delimiter
        self.cityNameGetter = cityNameGetter
        self.institutionNameGetter = institutionNameGetter
        self.unparsedInstitutions = {}


    def yieldFromFile(self, fileName):
        logger.info(u"Import street index data from csv file %s" % fileName)

        dictReader = csv.DictReader(open(fileName, "rt"), delimiter = self.delimiter)

        processed = 0
        rowNumber = 0
        numberFrom = u""
        numberTo = u""
        numberOdd = None
        
        for row in dictReader:
            rowNumber += 1
            municipality = readRow(row, "municipality")
            civilParish = readRow(row, "civilparish")
            city = self.cityNameGetter(row)
            street = readRow(row, "street")
            institutionKey = self.institutionNameGetter(row)
            yield (institutionKey, municipality, civilParish, city, street, numberFrom, numberTo, numberOdd)
            if city.strip() == u"":
               continue




    def yieldTerritories(self):
        for f in self.csvFileNames:
            f = os.path.join(os.getcwd(), f)
            for t in self.yieldFromFile(f):
                yield t

