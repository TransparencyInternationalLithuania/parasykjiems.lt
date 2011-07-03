import csv
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models.query_utils import Q
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName, InstitutionCivilparishMembers, InstitutionMunicipalityCode
from contactdb.models import Institution, PersonPosition, Person
from pjutils.exc import ChainnedException
from cdb_lt.personUtils import splitIntoNameAndSurname
from django.http import HttpResponse

class FieldNotDefinedInDataFile(ChainnedException):
    pass

class DuplicatePersonException(ChainnedException):
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
    if object is None:
        return None
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
        activePersonsFilter = PersonPosition.getFilterActivePositions()
        for chunk in chunks:
            personPositions = list(PersonPosition.objects.filter(institution__id__in = chunk).filter(activePersonsFilter) \
                .order_by('electedTo').select_related("person"))
            self.addToCache(personPositions)

class PersonCacheByName:
    def __init__(self):
        # holds person caches with disambiguation
        self.disambiguationCache = {}
        # holds any found duplicates with disambiguation
        self.duplicateDisambiguationCache = {}

        # holds name caches (i.e. withoud disambiguation columns)
        self.nameCache = {}
        # holds any found duplicates without disambiguation column
        self.duplicateNamesCache = {}

    def _getKey(self, name, surname, disambiguation = None):
        if disambiguation is None or disambiguation == u"":
            return "%s - %s" % (name, surname)
        return "%s - %s - %s" % (name, surname, disambiguation)

    def getByName(self, name, surname, disambiguation):
        key = self._getKey(name, surname, disambiguation)
        if not self.disambiguationCache.has_key(key): return None
        return self.disambiguationCache[key]
    
    def addToDuplicateCache(self, cache, person):
        key = self._getKey(person.name, person.surname, person.disambiguation)
        if not cache.has_key(key):
            cache[key] = []
        cache[key].append(person)

    def addToDuplicateCacheName(self, person):
        key = self._getKey(person.name, person.surname)
        if not self.duplicateNamesCache.has_key(key):
            self.duplicateNamesCache[key] = []
        self.duplicateNamesCache[key].append(person)

    def getOrCreatePerson(self, name, surname, disambiguation):
        dkey = self._getKey(name, surname, disambiguation)
        if self.disambiguationCache.has_key(dkey):
            return self.disambiguationCache[dkey]
        if self.duplicateDisambiguationCache.has_key(dkey):
            raise DuplicatePersonException("There are several persons with name %s %s %s" % (name, surname, disambiguation))

        key = self._getKey(name, surname)
        if self.duplicateNamesCache.has_key(key):
            raise DuplicatePersonException("There are several persons with name %s %s, and without disambiguation" % (name, surname))
        if self.nameCache.has_key(key):
            if disambiguation is not None and disambiguation != u"":
                raise DuplicatePersonException("""There is a person with name %s %s, but you requested to get persono
with disambiguation %s. So please fix database, add disambiguation to this person first. This will ensure data integrity""" % (name, surname, disambiguation))
            return self.nameCache[key]

        # there is no person is namesCache, nor in DisambinguationCache. So create a new one , and return it
        p = Person()
        p.name = name
        p.surname = surname
        p.disambiguation = disambiguation
        # just for debugging. remove this, not needed
        p.uniqueKey = "99999999"
        p.save()
        return p



    def addToCache(self, persons):
        for p in persons:
            # add to disambiguationCache
            dupkey = self._getKey(p.name, p.surname, p.disambiguation)
            if self.disambiguationCache.has_key(dupkey):
                self.addToDuplicateCache(self.duplicateDisambiguationCache, self.disambiguationCache[dupkey])
                del self.disambiguationCache[dupkey]
                self.addToDuplicateCache(self.duplicateDisambiguationCache, p)
                continue
            self.disambiguationCache[dupkey] = p

            key = self._getKey(p.name, p.surname)
            if self.nameCache.has_key(dupkey):
                self.addToDuplicateCacheName(self.nameCache[key])
                del self.nameCache[key]
                self.addToDuplicateCacheName(self.duplicateDisambiguationCache, p)
                continue
            self.nameCache[key] = p




    def loadAllWithName(self, nameAndSurnameTuples):
        step = 30
        chunks = [nameAndSurnameTuples[i:i+step] for i in range(0, len(nameAndSurnameTuples), step)]
        for chunk in chunks:
            queries = [Q(**{"name":name, "surname" : surname}) for name, surname, disambiguation in chunk]
            finalQuery = queries[0]
            for q in queries[1:]:
                finalQuery = finalQuery | q
            persons = list(Person.objects.filter(finalQuery))
            self.addToCache(persons)

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

            if not val.has_key(u"disambiguation"):
                val[u"disambiguation"] = u""

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
        if originalValue is not None:
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
        # loop through given attributes
        for key, attribute in keysToProperties.iteritems():
            v = row[key]
            # get the new value
            if type(v) is not dict:
                # if it is not a dict, then just take the value
                newV = v
            else:
                # else take the new value from dict
                newV = v[u'changed']
            # get old attribute value from object, and compare to new
            prevV = getattr(object, attribute)
            if prevV == newV:
                continue
            # values has  changed, update it
            setattr(object, attribute, newV)
            #changed = True

        # do not save, even if changed. will do that manually in outer loop
        #if changed:
        #    object.save()

    def _getPreviousAndCurrentValues(self, row, key):
        if not row.has_key(key): return None, None
        val = row[key]
        if type(val) is dict:
            return val['previous'], val[u'changed']
        return val, val

    @transaction.commit_on_success
    def updateDbWithNewData(self):
        errorList = []


        # cache all person objects with proposed names in csv file
        self.personCacheByName = PersonCacheByName()
        self.personCacheByName.loadAllWithName(self.nameAndSurnameTuples)


        for row in self.memberList:
            # search for institution object using supplied institution name
            institutionName = row[u"institutionName"]
            if not self.institutionCache.cache.has_key(institutionName):
                message = u'Institution with name "%s" not found' % institutionName
                errorList.append(message)
                continue
            institutionObj = self.institutionCache.cache[institutionName]

            # get reference to latest active personPosition for that institution
            previousPersonPosition = None
            if self.personPositionCache.cache.has_key(institutionObj.id):
                previousPersonPosition = self.personPositionCache.cache[institutionObj.id]

            # It is perfectly normal to not have a personPosition for an institution at all.
            # This happens when no representative exists when data is first time created
            #if previousPersonPosition is None:
            #    raise Exception("Did not find previous person position for insitution '%s'. Should never happen, or programming fault" % institutionName)
            previousPerson = getOrDefault(previousPersonPosition, u"person")

            # get previous and current values for name, surname and disambiguation
            previousName, name = self._getPreviousAndCurrentValues(row, u"name")
            previousSurname, surname = self._getPreviousAndCurrentValues(row, u"surname")
            previousDisambiguation, disambiguation = self._getPreviousAndCurrentValues(row, u"disambiguation")


            # either get existing personPosition, or create new one, depending on what is name and surname
            action = None
            if row.has_key(u"action"):
                action = row[u"action"]
            if action != "update":
                if previousPersonPosition is None:
                    latestActivePersonPosition = PersonPosition()
                    latestActivePersonPosition.institution = institutionObj
                    latestActivePerson = self.personCacheByName.getOrCreatePerson(name, surname, disambiguation)
                    latestActivePersonPosition.person = latestActivePerson
                    latestActivePersonPosition.save()
                elif previousPerson is None:
                    # we have an existing personPosition, but it had not attached Person object.
                    # so just create it
                    latestActivePersonPosition = previousPersonPosition
                    latestActivePerson = self.personCacheByName.getOrCreatePerson(name, surname, disambiguation)
                    latestActivePersonPosition.person = latestActivePerson
                    latestActivePersonPosition.save()
                elif previousName != name or previousSurname != surname or previousDisambiguation != disambiguation:
                    # if any of values for name, surname or disambiguation are different
                    # then we need to create new personPosition
                    latestActivePersonPosition = PersonPosition()
                    latestActivePersonPosition.institution = institutionObj
                    latestActivePerson = self.personCacheByName.getOrCreatePerson(name, surname, disambiguation)
                    latestActivePersonPosition.person = latestActivePerson
                    latestActivePersonPosition.save()
                else:
                    # everything is similar, just update existing person
                    latestActivePersonPosition = previousPersonPosition
            else:
                # this is an update action. This means that we will have to update even name and surname values
                # and not create new person.
                latestActivePersonPosition = previousPersonPosition

                # update name and surname
                latestActivePerson = latestActivePersonPosition.person
                latestActivePerson.name = name
                latestActivePerson.surname = surname
                latestActivePerson.save()


            latestActivePerson = getOrDefault(latestActivePersonPosition, u"person")
            if latestActivePerson is None:
                raise Exception("Did not find previous person for insitution '%s'. Should never happen, or programming fault" % institutionName)

            # update data now as we have found everything we need

            self.updateAndSaveIfChanged(row, institutionObj, {u"officeaddress":u"officeAddress",
                                                              u"officephone": u"officePhone"} )



            self.updateAndSaveIfChanged(row, latestActivePersonPosition, {u"officephone":u"primaryPhone",
                                                              u"email": u"email"} )

            if latestActivePersonPosition.electedFrom is None:
                latestActivePersonPosition.electedFrom = datetime.now()


            if latestActivePersonPosition != previousPersonPosition and previousPersonPosition is not None:
                previousPersonPosition.electedTo = datetime.now() + timedelta(days=-1)

            institutionObj.save()
            latestActivePersonPosition.save()
            if previousPersonPosition is not None:
                previousPersonPosition.save()

            #newPersonPosition.primaryPhone
            
            """self.updateIfChanged(row, u"name", row[u"name"], getOrDefault(previousPerson, u"name"))
            self.updateIfChanged(row, u"surname", row[u"surname"], getOrDefault(previousPerson, u"surname"))
            self.updateIfChanged(row, u"officephone", row[u"officephone"], getOrDefault(previousPersonPosition, u"officePhone"))
            self.updateIfChanged(row, u"email", row[u"email"], getOrDefault(previousPersonPosition, u"email"))"""
            # just update a single row for now
        for v in self.personCacheByName.duplicateNamesCache.itervalues():
            s = u""
            for i in v:
                s = "%s\n%s" % (s, u"%s %s" % (i.person.name, i.person.surname))
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
        self.nameAndSurnameTuples = [(val[u"name"], val[u"surname"], val[u"disambiguation"]) for val in self.memberList]

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
            changed = changed | self.updateIfChanged(row, u"disambiguation", row[u"disambiguation"], getOrDefault(previousPerson, u"disambiguation"))
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
        return errorList
