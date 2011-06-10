import csv
import os
from django.shortcuts import render_to_response
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName
from cdb_lt.personUtils import splitIntoNameAndSurname
from contactdb.models import Institution, Person, PersonPosition
from pjutils.exc import ChainnedException
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
    fileName = os.path.join(os.path.realpath(os.path.curdir), "static", "data", "update", "seniunai.csv")
    if not os.path.exists(fileName):
        params = {u"ErrorMessage" : "Civil parish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    memberList = readCsvFile(fileName, institutionType = u"civpar", institutionNameGetter=makeCivilParishInstitutionName)
    addChangedFields(memberList)
    headers = getHeaders(memberList)

    params = {u"headers" : headers, u"newData" : memberList}
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
    return getattr(dictionary[key], property, None)

def addChangedFields(memberList):
    for row in memberList:
        institutionName = row[u"institutionName"]
        institutionType = row[u"institutionType"]
        try:
            institutionId = Institution.objects.filter(institutionType__code = institutionType) \
                .filter(name=institutionName).get()
            row[u"institutionObj"] = institutionId
        except Institution.DoesNotExist:
            print u"Institution with name %s and code %s could not be found" % (institutionName, institutionType)
            continue

        try:
            row[u"previousPersonPosition"] = institutionId.personposition_set.get()
        except PersonPosition.DoesNotExist:
            row[u"previousPersonPosition"] = None
        row[u"previousPerson"] = getOrDefault(row, u"previousPersonPosition", u"person")


        updateIfChanged(row, u"name", row[u"name"], getOrDefault(row, u"previousPerson", u"name"))
        updateIfChanged(row, u"surname", row[u"surname"], getOrDefault(row, u"previousPerson", u"surname"))
        updateIfChanged(row, u"institutionName", row[u"institutionName"], row[u"institutionObj"].name)
        updateIfChanged(row, u"officephone", row[u"officephone"], getOrDefault(row, u"previousPersonPosition", u"primaryPhone"))
        updateIfChanged(row, u"officeaddress", row[u"officeaddress"], row[u"institutionObj"].officeAddress)

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
    addChangedFields(newMayorList)
    headers = getHeaders(newMayorList)

    params = {u"headers" : headers, u"newData" : newMayorList}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))
