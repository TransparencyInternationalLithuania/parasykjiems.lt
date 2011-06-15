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


civilParishStatic = os.path.join("data", "upload", "seniunai.csv")
civilParishFileName = os.path.join(os.path.realpath(os.path.curdir), "static", civilParishStatic)
mayorStatic = os.path.join("data", "upload", "merai.csv")
mayorCsv = os.path.join(os.path.realpath(os.path.curdir), "static", mayorStatic)

relativeUploadDir = os.path.join("data", "upload")
realUploadDir = os.path.join(STATIC_DOC_ROOT, "data", "upload")
dir_util.mkpath(realUploadDir)

def getNonExistentFileName(rootDir, originalFileName):
    name = os.path.join(rootDir, originalFileName)
    if not os.path.exists(name):
        return originalFileName
    basename, extension = os.path.splitext(originalFileName)
    num = 1
    while True:
        name = "%s-%s%s" % (basename, num, extension)
        realName = os.path.join(rootDir, name)
        if not os.path.exists(realName):
            return name
        num += 1

def writeUploadedFile(file):
    """ Writes uploaded file to disk, and returns file name used to store it"""
    fileName = getNonExistentFileName(rootDir=realUploadDir, originalFileName=file.name)
    realName = os.path.join(realUploadDir, fileName)
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
    return HttpResponseRedirect('/data/update/upload/%s/' % returnedFileName)



def diffUploadedFile(request, fileName, institutionType = None):
    relativeUploadFile, realUploadedFile = constructUploadedFileName(fileName)

    if not os.path.exists(realUploadedFile):
        params = {u"ErrorMessage" : "Uploaded file '%s'  does not exist, please upload it first." % relativeUploadFile}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(realUploadedFile, institutionType = institutionType)
    differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(),
              u"newData" : differ.memberList,
              u"errorList" : differ.errorList,
              u"diffAsCsvUrl" : u"/data/update/upload/%s/csv/" % fileName,
              u"importUrl" : u"/data/update/import/%s/" % fileName,
              u"originalCsvUrl" : constructAttachmentUrl(relativeUploadFile)}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))


def civilParishUpdate(request):
    return diffUploadedFile(request, fileName="seniunai.csv")
    """elapsedTime = TimeMeasurer()
    if not os.path.exists(civilParishFileName):
        params = {u"ErrorMessage" : "Civil parish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(civilParishFileName, institutionType = u"civpar")
    differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(),
              u"newData" : differ.memberList,
              u"errorList" : differ.errorList,
              u"diffAsCsvUrl" : u"/data/update/civilparish/csv/",
              u"originalCsvUrl" : constructAttachmentUrl(civilParishStatic)}
    response = render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))
    print u"generated in %s seconds" % elapsedTime.ElapsedSeconds()
    return response"""

def diffUploadedFileAsCsv(request, fileName, institutionType = None):
    relativeUploadFile = os.path.join(relativeUploadDir, fileName)
    realUploadedFile = os.path.join(os.path.realpath(os.path.curdir), "static", relativeUploadFile)
    if not os.path.exists(realUploadedFile):
        params = {u"ErrorMessage" : "Uploaded file '%s'  does not exist, please upload it first." % relativeUploadFile}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(realUploadedFile, institutionType = institutionType)
    differ.addChangedFields()

    return differ.asCsvToResponse(fileName)

def civilParishUpdateAsCsv(request):
    return diffUploadedFileAsCsv(request, fileName="seniunai.csv")
    """if not os.path.exists(civilParishFileName):
        params = {u"ErrorMessage" : "CivilParish file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(civilParishFileName, institutionType = u"civpar")
    differ.addChangedFields()

    return differ.asCsvToResponse("civilparish.csv")"""

def mayorUpdateAsCsv(request):
    return diffUploadedFileAsCsv(request, fileName="merai.csv")
    """if not os.path.exists(mayorCsv):
        params = {u"ErrorMessage" : "Mayor file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(mayorCsv, institutionType = u"mayor", institutionNameGetter=makeMunicipalityInstitutionName)
    differ.addChangedFields()

    return differ.asCsvToResponse("mayor.csv")"""

def constructUploadedFileName(fileName):
    relativeUploadFile = os.path.join(relativeUploadDir, fileName)
    realUploadedFile = os.path.join(os.path.realpath(os.path.curdir), "static", relativeUploadFile)
    return relativeUploadFile, realUploadedFile


def importUploadedFile(request, fileName, institutionType = None):
    relativeUploadFile, realUploadedFile = constructUploadedFileName(fileName)
    
    if not os.path.exists(realUploadedFile):
        params = {u"ErrorMessage" : "Uploaded file '%s'  does not exist, please upload it first." % relativeUploadFile}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(realUploadedFile, institutionType = institutionType)
    differ.addChangedFields()
    errorList = differ.updateDbWithNewData()

    params = {"errorList" : errorList,
              u"diffUrl" : u"/data/update/upload/%s/" % fileName}
    return render_to_response('cdb_lt/update/importSuccess.html', joinParams(params))
    
def mayorUpdate(request):
    return diffUploadedFile(request, "merai.csv")

    """if not os.path.exists(mayorCsv):
        params = {u"ErrorMessage" : "Mayor file does not exist, please upload it first."}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(mayorCsv, institutionType = u"mayor")
    differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(),
              u"newData" : differ.memberList,
              u"errorList" : differ.errorList,
              u"diffAsCsvUrl" : u"/data/update/mayor/csv/",
              u"originalCsvUrl" : constructAttachmentUrl(mayorStatic)}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))"""
