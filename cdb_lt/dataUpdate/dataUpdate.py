import csv
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName
from contactdb.models import Institution, PersonPosition
from pjutils.exc import ChainnedException
from cdb_lt.personUtils import splitIntoNameAndSurname
from django.http import HttpResponse

class FieldNotDefinedInDataFile(ChainnedException):
    pass

def toUnicode(val):
    return unicode(val, 'utf-8')

def deduceInstitutionNameGetter(institutionType):
    """ There are a limited set of defined institutionTypes.
    See createTerritories.py file for defined types.

    Returns a function which constructs institutionName """
    if institutionType == u"mayor":
        return makeMunicipalityInstitutionName
    elif institutionType == u"civpar":
        return makeCivilParishInstitutionName
    return None

class InstitutionCache:
    def __init__(self):
        self.cache = {}

    def addToCache(self, institutions):
        for i in institutions:
            self.cache[i.name] = i

    def loadAllWithName(self, institutionNames, institutionType):
        step = 30
        chunks = [institutionNames[i:i+step] for i in range(0, len(institutionNames), step)]
        for chunk in chunks:
            institutions = list(Institution.objects.filter(institutionType__code = institutionType) \
                .filter(name__in=chunk))
            self.addToCache(institutions)

def getOrDefault(object, property):
    return getattr(object, property, u"")


class PersonPositionCache:
    def __init__(self):
        self.cache = {}

    def addToCache(self, personPositions):
        for p in personPositions:
            self.cache[p.institution_id] = p

    def loadAllWithInstitutionId(self, institutionIds):
        step = 30
        chunks = [institutionIds[i:i+step] for i in range(0, len(institutionIds), step)]
        for chunk in chunks:
            personPositions = list(PersonPosition.objects.filter(institution__id__in = chunk).select_related("person"))
            self.addToCache(personPositions)

class DataUpdateDiffer:
    oldColumnSuffix = u"_old"

    def __init__(self, fileName, institutionType = None, institutionNameGetter = None):
        self.memberList = self._readCsvFile(fileName=fileName, institutionType=institutionType, institutionNameGetter=institutionNameGetter)
        self.changedFields = {}

    def _readCsvFile(self, fileName, institutionType = None, institutionNameGetter = None):
        """ Reads a generic csv file, and builds a list of rows, where
        each row is a dictionary with data

        institutionType is used to distinguish which institution are we importing here. If csv file does not contain
        "institutionType" column, then you must pass institutionType. This will be used to deduce which institutionNameGetter
        to use. 

        institutionNameGetter is used to construct institutionName field, which is an aggregate of several fields usually.
        Can be passed as None, in which case it will be deduced automatically"""
        newMayorList = []

        for row in csv.DictReader(open(fileName, "rt")):
            val = dict([(toUnicode(key), toUnicode(val)) for key, val in row.iteritems()])

            if val.has_key(u"fullname"):
                val[u"name"], val[u"surname"] = splitIntoNameAndSurname(val[u"fullname"])
                del val[u"fullname"]

            if institutionType is not None:
                val[u"institutionType"] = institutionType
            else:
                if not val.has_key(u"institutionType"):
                    raise FieldNotDefinedInDataFile(u"No institution type defined for row: %s" % row)

            institutionNameGetter = deduceInstitutionNameGetter(val[u"institutionType"])

            if institutionNameGetter is not None:
                name = institutionNameGetter(row)
                val[u"institutionName"] = name
            else:
                if not val.has_key(u"institutionName"):
                    raise FieldNotDefinedInDataFile(u"No institutionName defined for row: %s" % row)

            newMayorList.append(val)
        return newMayorList

    def getHeaders(self):
        if not len(self.memberList):
            return []
        return self.memberList[0].keys()

    def getHeadersWithChangedFields(self):
        return self.changedFields.keys()

    def updateIfChanged(self, row, key, newValue, originalValue):
        if originalValue == newValue:
            return
        d = {u"previous": originalValue,
             u"changed": newValue}
        row[key] = d
        self.changedFields[key] = key

    def _buildUpChangedHeaders(self, originalHeaders, changedHeaders):
        headers = originalHeaders
        for k in changedHeaders:
            header = "%s%s" % (k, DataUpdateDiffer.oldColumnSuffix)
            headers.append(header)
        return headers

    def asCsvToResponse(self, attachmentName):
        """ writes all member data as csv file to a response object and returns it.

        Columns which have changed value will be split into two columns with names: columnName and columnName_new

        Second column will contain new, proposed value
        """
        
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % attachmentName

        headers = self._buildUpChangedHeaders(self.getHeaders(), self.getHeadersWithChangedFields())
        headers.sort()
        writer = csv.DictWriter(response, fieldnames=headers, extrasaction='ignore')
        writer.writerow(dict((k, k) for k in headers))

        for row in self.memberList:
            for key, val in row.items():
                if type(val) is dict:
                    keyold = u"%s%s" % (key, DataUpdateDiffer.oldColumnSuffix)
                    row[key] = val[u'changed'].encode('utf-8')
                    row[keyold] = val['previous'].encode('utf-8')
                else:
                    row[key] = val.encode('utf-8')
            writer.writerow(row)
        return response

    def removeOldColumns(self, row):
        """ When csv file gets downloaded as diff, new columns are added, which hold old values.
        These columns should be removed, as otherwise there will be more and more
        such new columns added """
        keys = row.keys()
        for k in keys:
            if not k.endswith(DataUpdateDiffer.oldColumnSuffix):
                continue
            previousKey = k.rstrip(DataUpdateDiffer.oldColumnSuffix)
            if row.has_key(previousKey):
                #remove item with new key.  
                del row[k]
        

    def addChangedFields(self):
        errorList = []
        institutionCache = InstitutionCache()
        institutionNames = [row[u"institutionName"] for row in self.memberList]
        institutionCache.loadAllWithName(institutionNames, institutionType= self.memberList[0][u"institutionType"])

        personPositionCache = PersonPositionCache()
        institutionIds = [i.id for i in institutionCache.cache.values()]
        personPositionCache.loadAllWithInstitutionId(institutionIds)

        for row in self.memberList:
            institutionName = row[u"institutionName"]
            if not institutionCache.cache.has_key(institutionName):
                message = u'Institution with name "%s" not found' % institutionName
                errorList.append(message)
                continue

            institutionObj = institutionCache.cache[institutionName]

            previousPersonPosition = None
            if personPositionCache.cache.has_key(institutionObj.id):
                previousPersonPosition = personPositionCache.cache[institutionObj.id]
            previousPerson = getOrDefault(previousPersonPosition, u"person")


            self.updateIfChanged(row, u"name", row[u"name"], getOrDefault(previousPerson, u"name"))
            self.updateIfChanged(row, u"surname", row[u"surname"], getOrDefault(previousPerson, u"surname"))
            self.updateIfChanged(row, u"institutionName", row[u"institutionName"], institutionObj.name)
            self.updateIfChanged(row, u"officephone", row[u"officephone"], getOrDefault(previousPersonPosition, u"primaryPhone"))
            self.updateIfChanged(row, u"officeaddress", row[u"officeaddress"], institutionObj.officeAddress)

            self.removeOldColumns(row)

        self.errorList = errorList
