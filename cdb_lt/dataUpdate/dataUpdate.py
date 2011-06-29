import csv
from django.db.models.query_utils import Q
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName, InstitutionCivilparishMembers, InstitutionMunicipalityCode
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
    if institutionType == InstitutionMunicipalityCode:
        return makeMunicipalityInstitutionName
    elif institutionType == InstitutionCivilparishMembers:
        return makeCivilParishInstitutionName
    raise Exception("Unknown institution type '%s'. Check that source file contains valid institution type" % institutionType)

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

class PersonPositionCacheByName:
    def __init__(self):
        self.cache = {}
        self.duplicatesCache = {}

    def _getKey(self, name, surname):
        return "%s - %s" % (name, surname)

    def getByName(self, name, surname):
        key = self._getKey(name, surname)
        if not self.cache.has_key(key): return None
        return self.cache[key]
    
    def addToDuplicateCache(self, personPosition):
        key = self._getKey(personPosition.person.name, personPosition.person.surname)
        if not self.duplicatesCache.has_key(key):
            self.duplicatesCache[key] = []
        self.duplicatesCache[key].append(personPosition)


    def addToCache(self, personPositions):
        for p in personPositions:
            key = self._getKey(p.person.name, p.person.surname)
            if self.cache.has_key(key):
                self.addToDuplicateCache(self.cache[key])
                del self.cache[key]
                self.addToDuplicateCache(p)
                continue
            self.cache[key] = p

    def loadAllWithName(self, nameAndSurnameTuples):
        step = 30
        chunks = [nameAndSurnameTuples[i:i+step] for i in range(0, len(nameAndSurnameTuples), step)]
        for chunk in chunks:
            queries = [Q(**{"person__name":name, "person__surname" : surname}) for name, surname in chunk]
            finalQuery = queries[0]
            for q in queries[1:]:
                finalQuery = finalQuery | q
            personPositions = list(PersonPosition.objects.filter(finalQuery).select_related("person"))
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
        """ Replaces row value with dictionary containing old and new values, if they are different.
        Returns true if values are different. Retuerns False if did not change anything"""
        newValue = newValue.strip()
        originalValue = originalValue.strip()
        if originalValue == newValue:
            return False
        d = {u"previous": originalValue,
             u"changed": newValue}
        row[key] = d
        self.changedFields[key] = key
        return True

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
        length = len(DataUpdateDiffer.oldColumnSuffix)
        for k in keys:
            if not k.endswith(DataUpdateDiffer.oldColumnSuffix):
                continue
            previousKey = k[0:-length]
            if row.has_key(previousKey):
                #remove item with new key.  
                del row[k]

    def updateAndSaveIfChanged(self, row, object, keysToProperties):
        changed = False
        for key, attribute in keysToProperties.iteritems():
            v = row[key]
            if type(v) is not dict:
                continue
            changed = True
            setattr(object, attribute, v[u'changed'])
        if changed:
            object.save()

    def _getPreviousAndCurrentValues(self, row, key):
        if not row.has_key(key): return None, None
        val = row[key]
        if type(val) is dict:
            return val['previous'], val[u'changed']
        return val, val

    def updateDbWithNewData(self):
        errorList = []


        # cachce all person position objects with proposed names in csv file
        self.newPersonPositionCache = PersonPositionCacheByName()
        self.newPersonPositionCache.loadAllWithName(self.nameAndSurnameTuples)



        for row in self.memberList:
            institutionName = row[u"institutionName"]
            if not self.institutionCache.cache.has_key(institutionName):
                message = u'Institution with name "%s" not found' % institutionName
                errorList.append(message)
                continue

            institutionObj = self.institutionCache.cache[institutionName]
            previousPersonPosition = None
            if self.personPositionCache.cache.has_key(institutionObj.id):
                previousPersonPosition = self.personPositionCache.cache[institutionObj.id]
            previousPerson = getOrDefault(previousPersonPosition, u"person")



            self.updateAndSaveIfChanged(row, institutionObj, {u"officeaddress":u"officeAddress",
                                                              u"officephone": u"officePhone"} )

            previousName, name = self._getPreviousAndCurrentValues(row, u"name")
            previousSurname, surname = self._getPreviousAndCurrentValues(row, u"surname")

            newPersonPosition = self.newPersonPositionCache.getByName(name, surname)
            if newPersonPosition is None:
                # there is no PersonPosition in the db with new Name and Surname
                # create one
                continue


            self.updateAndSaveIfChanged(row, newPersonPosition, {u"officephone":u"officePhone",
                                                              u"email": u"email"} )
            #newPersonPosition.primaryPhone
            
            """self.updateIfChanged(row, u"name", row[u"name"], getOrDefault(previousPerson, u"name"))
            self.updateIfChanged(row, u"surname", row[u"surname"], getOrDefault(previousPerson, u"surname"))
            self.updateIfChanged(row, u"officephone", row[u"officephone"], getOrDefault(previousPersonPosition, u"officePhone"))
            self.updateIfChanged(row, u"email", row[u"email"], getOrDefault(previousPersonPosition, u"email"))"""
        return errorList

        

    def addChangedFields(self):
        """ Loops over loaded csv file, and compares the data against database.
        If field values have changed, replaces value with a dictionary containing old and new value.

        Populates institutionCache and personPositionCache with data from database.  

        """
        errorList = []
        # cache all instituion objects with the same name, as specified in csv file
        self.institutionCache = InstitutionCache()
        institutionNames = [row[u"institutionName"] for row in self.memberList]
        self.institutionCache.loadAllWithName(institutionNames, institutionType= self.memberList[0][u"institutionType"])

        # cache all person position objects existing in DB, related to self.institutionCache
        self.personPositionCache = PersonPositionCache()
        institutionIds = [i.id for i in self.institutionCache.cache.values()]
        self.personPositionCache.loadAllWithInstitutionId(institutionIds)

        # hold a copy of names and tuples from csv file
        self.nameAndSurnameTuples = [(val[u"name"], val[u"surname"]) for val in self.memberList]

        changedRows = []

        for row in self.memberList:
            institutionName = row[u"institutionName"]
            if not self.institutionCache.cache.has_key(institutionName):
                message = u'Institution with name "%s" not found' % institutionName
                errorList.append(message)
                continue

            institutionObj = self.institutionCache.cache[institutionName]

            previousPersonPosition = None
            if self.personPositionCache.cache.has_key(institutionObj.id):
                previousPersonPosition = self.personPositionCache.cache[institutionObj.id]
            previousPerson = getOrDefault(previousPersonPosition, u"person")


            changed = False
            changed = changed | self.updateIfChanged(row, u"name", row[u"name"], getOrDefault(previousPerson, u"name"))
            changed = changed | self.updateIfChanged(row, u"surname", row[u"surname"], getOrDefault(previousPerson, u"surname"))
            #changed = changed | self.updateIfChanged(row, u"institutionName", row[u"institutionName"], institutionObj.name)
            changed = changed | self.updateIfChanged(row, u"officephone", row[u"officephone"], getOrDefault(institutionObj, u"officePhone"))
            changed = changed | self.updateIfChanged(row, u"email", row[u"email"], getOrDefault(previousPersonPosition, u"email"))
            changed = changed | self.updateIfChanged(row, u"officeaddress", row[u"officeaddress"], institutionObj.officeAddress)

            if changed:
                changedRows.append(row)
            self.removeOldColumns(row)

        self.memberList = changedRows
        self.errorList = errorList
