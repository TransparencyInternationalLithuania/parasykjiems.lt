import csv
import os
from django.shortcuts import render_to_response
from cdb_lt.dataUpdate.dataUpdate import DataUpdateDiffer
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName
from pjutils.timemeasurement import TimeMeasurer
from settings import GlobalSettings

defaultParams = {
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    }

def joinParams(params):
    viewParams = defaultParams.copy()
    viewParams.update(params)
    return viewParams

civilParishFileName = os.path.join(os.path.realpath(os.path.curdir), "static", "data", "update", "seniunai.csv")
mayorCsv = os.path.join(os.path.realpath(os.path.curdir), "static", "data", "update", "merai.csv")

def civilParishUpdate(request):
    elapsedTime = TimeMeasurer()
    if not os.path.exists(civilParishFileName):
        params = {u"ErrorMessage" : "Civil parish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(civilParishFileName, institutionType = u"civpar", institutionNameGetter=makeCivilParishInstitutionName)
    differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(), u"newData" : differ.memberList, u"errorList" : differ.errorList}
    response = render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))
    print u"generated in %s seconds" % elapsedTime.ElapsedSeconds()
    return response

def civilParishUpdateAsCsv(request):
    if not os.path.exists(civilParishFileName):
        params = {u"ErrorMessage" : "CivilParish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(civilParishFileName, institutionType = u"civpar", institutionNameGetter=makeCivilParishInstitutionName)
    differ.addChangedFields()

    return differ.asCsvToResponse("civilparish.csv")


def mayorUpdateAsCsv(request):
    if not os.path.exists(mayorCsv):
        params = {u"ErrorMessage" : "Mayor file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(mayorCsv, institutionType = u"mayor", institutionNameGetter=makeMunicipalityInstitutionName)
    differ.addChangedFields()

    return differ.asCsvToResponse("mayor.csv")

def mayorUpdate(request):
    if not os.path.exists(mayorCsv):
        params = {u"ErrorMessage" : "Mayor file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(mayorCsv, institutionType = u"mayor", institutionNameGetter=makeMunicipalityInstitutionName)
    differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(), u"newData" : differ.memberList, u"errorList" : differ.errorList}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))
