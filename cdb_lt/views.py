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
    """ Shows a form where user can upload csv files, and store them on the server.
    If a file is posted, it is saved and then redirected to visual diff page"""
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
    """ shows a visual diff of the uploaded csv file as html. Columns with prefix *_old are removed"""
    relativeUploadFile, realUploadedFile = constructUploadedFileName(fileName)

    if not os.path.exists(realUploadedFile):
        params = {u"ErrorMessage" : "Uploaded file '%s'  does not exist, please upload it first." % relativeUploadFile}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(realUploadedFile, institutionType = institutionType)
    errorList = differ.addChangedFields()

    params = {u"headers" : differ.getHeaders(),
              u"newData" : differ.memberList,
              u"errorList" : errorList,
              u"diffAsCsvUrl" : u"/data/update/upload/%s/csv/" % fileName,
              u"importUrl" : u"/data/update/import/%s/" % fileName,
              u"originalCsvUrl" : constructAttachmentUrl(relativeUploadFile)}
    return render_to_response('cdb_lt/update/mayorUpdate.html', joinParams(params))

def importDocs(request):
    return render_to_response('cdb_lt/update/importDocumentation.html')

def civilParishUpdate(request):
    """ shows a visual diff of civil parish member file"""
    return diffUploadedFile(request, fileName="seniunai.csv")

def diffUploadedFileAsCsv(request, fileName, institutionType = None):
    """ Diffs any uploadded file, and returns it as csv file.
    This csv file contains combined data from original csv file, and data from database.
    Columns from database are prefixed with _old prefix, so user can later manually
    tweak the csv file, and choose whether he want to copy over old data over new one. This is needed
    in cases where new data is not correct, or not complete.

    Later this tweaked csv file can be uploaded again, and *_old columns will be ignored. This will allow
    to download diff as csv and upload it again any number of times.
    """
    relativeUploadFile = os.path.join(relativeUploadDir, fileName)
    realUploadedFile = os.path.join(os.path.realpath(os.path.curdir), "static", relativeUploadFile)
    if not os.path.exists(realUploadedFile):
        params = {u"ErrorMessage" : "Uploaded file '%s'  does not exist, please upload it first." % relativeUploadFile}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(realUploadedFile, institutionType = institutionType)
    differ.addChangedFields()

    return differ.asCsvToResponse(fileName)

def civilParishUpdateAsCsv(request):
    """ return civil parish diff as csv file, instead of displayig it as html
    """
    return diffUploadedFileAsCsv(request, fileName="seniunai.csv")

def mayorUpdateAsCsv(request):
    """ Return a mayor diff as csv file, instead of displaying it as html"""
    return diffUploadedFileAsCsv(request, fileName="merai.csv")

def constructUploadedFileName(fileName):
    relativeUploadFile = os.path.join(relativeUploadDir, fileName)
    realUploadedFile = os.path.join(os.path.realpath(os.path.curdir), "static", relativeUploadFile)
    return relativeUploadFile, realUploadedFile


def importUploadedFile(request, fileName, institutionType = None):
    """ Imports data from csv file into database, and renders an import success response
    """
    relativeUploadFile, realUploadedFile = constructUploadedFileName(fileName)
    
    if not os.path.exists(realUploadedFile):
        params = {u"ErrorMessage" : "Uploaded file '%s'  does not exist, please upload it first." % relativeUploadFile}
        return render_to_response('pjweb/error.html', joinParams(params))

    differ = DataUpdateDiffer(realUploadedFile, institutionType = institutionType)
    errorList = differ.addChangedFields()
    errorList2 = differ.updateDbWithNewData()

    params = {"errorList" : errorList + errorList2,
              u"diffUrl" : u"/data/update/upload/%s/" % fileName}
    return render_to_response('cdb_lt/update/importSuccess.html', joinParams(params))

def mayorUpdate(request):
    """ Mayor file is already uploaded. Show visual diff for it """
    return diffUploadedFile(request, "merai.csv")