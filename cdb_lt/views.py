from distutils import dir_util
import os
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from cdb_lt.dataUpdate.dataUpdate import DataUpdateDiffer
from cdb_lt.dataUpdate.dataUpload import UploadFileForm
from cdb_lt.management.commands.createMembers import makeCivilParishInstitutionName, makeMunicipalityInstitutionName
from pjutils.timemeasurement import TimeMeasurer
from settings import GlobalSettings
from settings_local import STATIC_DOC_ROOT

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

def constructAttachmentUrl(attachmentPath):
    current_site = Site.objects.get_current()
    path = "%s/%s" % ("static", attachmentPath)
    path = path.replace("\\", "/")
    return u"http://%s/%s" % (current_site.domain, path)


civilParishStatic = os.path.join("data", "update", "seniunai.csv")
civilParishFileName = os.path.join(os.path.realpath(os.path.curdir), "static", civilParishStatic)
mayorStatic = os.path.join("data", "update", "merai.csv")
mayorCsv = os.path.join(os.path.realpath(os.path.curdir), "static", mayorStatic)

def getNonExistentFileName(rootDir, originalFileName):
    name = os.path.join(rootDir, originalFileName)
    if os.path.exists(name) == False:
        return name
    basename, extension = os.path.splitext(originalFileName)
    num = 1
    while True:
        name = "%s-%s%s" % (basename, num, extension)
        realName = os.path.join(rootDir, name)
        if os.path.exists(realName) == False:
            return name
        num += 1

def writeUploadedFile(file):
    """ Writes uploaded file to disk, and returns file name used to store it"""
    rootDir = os.path.join(STATIC_DOC_ROOT, "dataUpload")
    dir_util.mkpath(rootDir)
    fileName = getNonExistentFileName(rootDir=rootDir, originalFileName=file.name)
    realName = os.path.join(rootDir, fileName)
    destination = open(realName, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    return fileName
    

def uploadData(request):
    if request.method != 'POST':
        form = UploadFileForm()
        return render_to_response('cdb_lt/update/upload.html', {'form': form})

    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        form = UploadFileForm()
        return render_to_response('cdb_lt/update/upload.html', {'form': form})

    returnedFileName = writeUploadedFile(request.FILES['csvFile'])
    return HttpResponseRedirect('/cdb_lt/update/upload/%s/' % returnedFileName)


def civilParishUpdate(request):
    elapsedTime = TimeMeasurer()
    if not os.path.exists(civilParishFileName):
        params = {u"ErrorMessage" : "Civil parish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(civilParishFileName, institutionType = u"civpar", institutionNameGetter=makeCivilParishInstitutionName)
    differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(),
              u"newData" : differ.memberList,
              u"errorList" : differ.errorList,
              u"csvUrl" : u"/data/update/civilparish/csv/",
              u"originalCsv" : constructAttachmentUrl(civilParishStatic)}
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

    params = {u"headers" : differ.getHeaders(),
              u"newData" : differ.memberList,
              u"errorList" : differ.errorList,
              u"csvUrl" : u"/data/update/mayor/csv/",
              u"originalCsv" : constructAttachmentUrl(mayorStatic)}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))
