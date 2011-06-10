import csv
import os
from django.shortcuts import render_to_response
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName
from cdb_lt.personUtils import splitIntoNameAndSurname
from contactdb.models import Institution, Person, PersonPosition
from pjutils.exc import ChainnedException
from pjutils.timemeasurement import TimeMeasurer
from settings import GlobalSettings

class FieldNotDefinedInDataFile(ChainnedException):
    pass

defaultParams = {
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    }

def toUnicode(val):
    return unicode(val, 'utf-8')

def updateIfChanged(row, key, newValue, originalValue):
    if originalValue == newValue:
        return
    d = {u"previous": originalValue,
         u"changed": newValue}
    row[key] = d

def joinParams(params):
    viewParams = defaultParams.copy()
    viewParams.update(params)
    return viewParams

def civilParishUpdate(request):
    elapsedTime = TimeMeasurer()
    fileName = os.path.join(os.path.realpath(os.path.curdir), "static", "data", "update", "seniunai.csv")
    if not os.path.exists(fileName):
        params = {u"ErrorMessage" : "Civil parish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    memberList = readCsvFile(fileName, institutionType = u"civpar", institutionNameGetter=makeCivilParishInstitutionName)
    errorList = addChangedFields(memberList)
    headers = getHeaders(memberList)

    params = {u"headers" : headers, u"newData" : memberList, u"errorList" : errorList}
    print u"generated in %s seconds" % elapsedTime.ElapsedSeconds()
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))

def readCsvFile(fileName, institutionType = None, institutionNameGetter = None):
    """ Reads a generic csv file, and builds a list of rows, where
    each row is a dictionary with data

    institutionType is used to distinguish which
    institutionNameGetter is used to construct institutionName field, which is an aggregate of several fields usually"""
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

        if institutionNameGetter is not None:
            name = institutionNameGetter(row)
            val[u"institutionName"] = name
        else:
            if not val.has_key(u"institutionName"):
                raise FieldNotDefinedInDataFile(u"No institutionName defined for row: %s" % row)

        newMayorList.append(val)
    return newMayorList

def getOrDefault(dictionary, key, property):
    if not dictionary.has_key(key):
        return None
    return getattr(dictionary[key], property, u"")


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

class PersonPositionCache:
    def __init__(self):
        self.cache = {}

    def addToCache(self, personPositions):
        for p in personPositions:
            self.cache[p.institution.id] = p

    def loadAllWithInstitutionId(self, institutionIds):
        step = 30
        chunks = [institutionIds[i:i+step] for i in range(0, len(institutionIds), step)]
        for chunk in chunks:
            personPositions = list(PersonPosition.objects.filter(institution__id__in = chunk).select_related("person"))
            self.addToCache(personPositions)




def addChangedFields(memberList):
    errorList = []
    institutionCache = InstitutionCache()
    institutionNames = [row[u"institutionName"] for row in memberList]
    institutionCache.loadAllWithName(institutionNames, institutionType= memberList[0][u"institutionType"])

    personPositionCache = PersonPositionCache()
    institutionIds = [i.id for i in institutionCache.cache.values()]
    personPositionCache.loadAllWithInstitutionId(institutionIds)

    for row in memberList:
        institutionName = row[u"institutionName"]
        if not institutionCache.cache.has_key(institutionName):
            message = u'Institution with name "%s" not found' % institutionName
            errorList.append(message)
            continue

        institutionObj = institutionCache.cache[institutionName]
        #row[u"institutionObj"] = institutionId

        """institutionType = row[u"institutionType"]
        try:
            institutionId = Institution.objects.filter(institutionType__code = institutionType) \
                .filter(name=institutionName).get()
            row[u"institutionObj"] = institutionId
        except Institution.DoesNotExist:
            message = u'Institution with name "%s" not found' % institutionName
            errorList.append(message)
            continue"""


        if personPositionCache.cache.has_key(institutionObj.id):
            row[u"previousPersonPosition"] = personPositionCache.cache[institutionObj.id]
        else:
            row[u"previousPersonPosition"] = None
        """try:
            row[u"previousPersonPosition"] = institutionObj.personposition_set.get()
        except PersonPosition.DoesNotExist:
            row[u"previousPersonPosition"] = None
        row[u"previousPerson"] = getOrDefault(row, u"previousPersonPosition", u"person")"""
        row[u"previousPerson"] = getOrDefault(row, u"previousPersonPosition", u"person")


        updateIfChanged(row, u"name", row[u"name"], getOrDefault(row, u"previousPerson", u"name"))
        updateIfChanged(row, u"surname", row[u"surname"], getOrDefault(row, u"previousPerson", u"surname"))
        updateIfChanged(row, u"institutionName", row[u"institutionName"], institutionObj.name)
        updateIfChanged(row, u"officephone", row[u"officephone"], getOrDefault(row, u"previousPersonPosition", u"primaryPhone"))
        updateIfChanged(row, u"officeaddress", row[u"officeaddress"], institutionObj.officeAddress)

    return errorList

def getHeaders(memberList):
    headers = []
    if len(memberList) > 0:
        headers = memberList[0].keys()
    return headers


def mayorUpdate(request):

    fileName = os.path.join(os.path.realpath(os.path.curdir), "static", "data", "update", "merai.csv")
    if not os.path.exists(fileName):
        params = {u"ErrorMessage" : "Mayor file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    newMayorList = readCsvFile(fileName, institutionType = u"mayor", institutionNameGetter=makeMunicipalityInstitutionName)
    errorList = addChangedFields(newMayorList)
    headers = getHeaders(newMayorList)

    params = {u"headers" : headers, u"newData" : newMayorList, u"errorList" : errorList}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))
