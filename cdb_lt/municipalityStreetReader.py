import csv
import os
from cdb_lt.management.commands.createMembers import ImportSourcesMembers
from contactdb.importUtils import readRow, getInstitutionNameFromColumn
import logging
logger = logging.getLogger(__name__)


class municipalityStreetReader(object):
    def __init__(self, delimiter=","):
        self.delimiter = delimiter
        self.institutionNameGetter = getInstitutionNameFromColumn
        self.unparsedInstitutions = {}


    def yieldTerritories(self):
        fileName = ImportSourcesMembers.LithuanianMunicipalityMembers
        logger.info(u"Import street index data from csv file %s" % fileName)

        dictReader = csv.DictReader(open(fileName, "rt"), delimiter = self.delimiter)

        processed = 0
        rowNumber = 0
        numberFrom = u""
        numberTo = u""
        numberOdd = None

        for row in dictReader:
            rowNumber += 1
            municipality = readRow(row, "institution")
            civilParish = u""
            city = u""
            street = u""
            institutionKey = self.institutionNameGetter(row)
            yield {"institutionKey" : institutionKey, "municipality" : municipality,
                           "civilParish" : civilParish, "city": city,
                           "street" : street, "numberFrom" : numberFrom,
                           "numberTo" : numberTo, "numberOdd": numberOdd,
                           "comment" : None}

