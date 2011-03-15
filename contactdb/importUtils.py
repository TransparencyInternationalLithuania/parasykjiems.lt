import csv
import os
from contactdb.models import Person, InstitutionType, Institution, PersonPosition
from pjutils.exc import ChainnedException

import logging
logger = logging.getLogger(__name__)
from django.db import connection, transaction

class ImportSourceNotExistsException(ChainnedException):
    pass

class InstitutionTypeDoesNotExist(ChainnedException):
    pass

class PersonPositionCache(object):

    def __init__(self, institutionCode):
        self.cache = {}

        sql = """select p.uniqueKey, i.name, it.code from contactdb_personposition pp
left join contactdb_person p on p.id = pp.person_id
left join contactdb_institution i on pp.institution_id = i.id
left join contactdb_institutiontype it on i.institutiontype_id = it.id
where it.code = '%s'
""" % institutionCode

        persons = PersonPosition.objects.all().filter(institution__institutionType__code = institutionCode)

        #cursor = connection.cursor()
        #val = cursor.execute(sql)

        for p in persons:
            key = self._makeKey(p.person.uniqueKey, p.institution.name)
            self.cache[key] = p

        transaction.commit_unless_managed()

    def _makeKey(self, uniqueKey, name):
        return "%s %s" % (uniqueKey, name)

    def getPersonPosition(self, uniqueKey, name):
        """ returns person position based on unique key"""
        key = self._makeKey(uniqueKey, name)
        if not self.cache.has_key(key):
            return None
        return self.cache[key]



def EnsureExists(importSource, downloadCommand = "downloadDocs"):
    """ Checks that a given import source exists on file system. if not, throw an exception,
     so that user would know how to donwload that source"""
    file = os.path.join(os.getcwd(), importSource)
    exists = os.path.exists(file)
    if not exists:
        raise ImportSourceNotExistsException("""File '%s' does not exist on your file system. Usually this means
that an appropriate google doc was not downloaded yet.  You can do that by calling manage.py %s """ % (file, downloadCommand))


def readRow(row, key, default = "throwException"):
    key = key.lower()
    key = key.replace("_", "")
    if row.has_key(key) == False:
        if default is not "throwException":
            return default
        
        logger.debug("Could not find value in csv row '%s'.  Will print now all possible keys:" % key)
        for p in row.iterkeys():
            logger.debug("key: '%s'" % p)
        row[key].strip()
    val = row[key]
    if val is None:
        return u""
    return unicode(val.strip(), 'utf-8')

def importPersons(csvFileName, delimiter = ","):
    """ Imports from csv file persons.
    Csv file must contain these csv fields:
    name,
    surname,
    uniquekey
    """
    EnsureExists(csvFileName)
    allRecords = os.path.join(os.getcwd(), csvFileName)
    dictReader = csv.DictReader(open(allRecords, "rt"), delimiter = delimiter)

    count = 0
    for row in dictReader:
        p = Person()
        p.id = readRow(row, "uniquekey")
        p.name = readRow(row, "name")
        p.surname = readRow(row,"surname")
        p.uniqueKey = readRow(row, "uniquekey")
        p.save()
        count+=1

    logger.info("Imported %s members" % count)


def createInstitutionType(code, name=None):
    if getInstitutionTypeWithCode(institutionCode=code) is not None:
        return
    it = InstitutionType()
    it.name = name
    it.code = code
    it.save()

def getInstitutionTypeWithCode(institutionCode):
    try:
        institutionType = InstitutionType.objects.filter(code=institutionCode).get()
        return institutionType
    except InstitutionType.DoesNotExist:
        return None

def getOrCreateInstitution(name, institutionType):
    try:
        return Institution.objects.all().filter(institutionType=institutionType) \
            .filter(name = name).get()
    except Institution.DoesNotExist:
        i = Institution()
        i.name = name
        i.institutionType = institutionType
        return i

def getPersonPosition(personUniqueCode, institutionName, institutionType):
    try:
        return PersonPosition.objects.all().filter(person__uniqueKey=personUniqueCode) \
            .filter(institution__name = institutionName) \
            .filter(institution__institutionType = institutionType).get()
    except PersonPosition.DoesNotExist:
        return None

def getOrCreatePerson(personUniqueCode):
    try:
        return Person.objects.all().filter(uniqueKey=personUniqueCode).get()
    except Person.DoesNotExist:
        p = Person()
        #p.id = personUniqueCode
        p.uniqueKey = personUniqueCode
        return p

@transaction.commit_on_success
def importInstitutionData(csvFileName, institutionCode, uniqueKeyStartsFrom, delimiter = ","):
    """ uniqueKeyStartsFrom defines the start number value of the uniqueKeyField """

    try:
        institutionType = getInstitutionTypeWithCode(institutionCode = institutionCode)
    except InstitutionType.DoesNotExist:
        raise InstitutionTypeDoesNotExist(message="Institution with type '%s' could not be found" % institutionCode)

    personPositionCache = PersonPositionCache(institutionCode = institutionCode)

    EnsureExists(csvFileName)
    allRecords = os.path.join(os.getcwd(), csvFileName)
    dictReader = csv.DictReader(open(allRecords, "rt"), delimiter = delimiter)


    institutionCount = 0
    for row in dictReader:
        uniquekey = int(readRow(row, "uniquekey")) + uniqueKeyStartsFrom
        institutionName = readRow(row, "institution")


        personPosition = personPositionCache.getPersonPosition(uniquekey, institutionName)
        #personPosition = getPersonPosition(personUniqueCode = uniquekey, institutionName = institutionName, institutionType=institutionType)
        if personPosition == None:
            personPosition = PersonPosition()
            personPosition.institution = getOrCreateInstitution(name=institutionName, institutionType = institutionType)
            personPosition.person = getOrCreatePerson(personUniqueCode = uniquekey)

        personPosition.institution.officePhone = readRow(row, "officePhone", default=u"")
        personPosition.institution.officeAddress = readRow(row,"officeAddress", default=u"")
        personPosition.institution.officeEmail = readRow(row,"officeEmail", default=u"")

        name = readRow(row, "name").strip()
        if name == "":
            continue
        personPosition.person.name = readRow(row, "name")
        personPosition.person.surname = readRow(row,"surname")

        personPosition.email = readRow(row,"email", default=u"")

        personPosition.person.save()
        personPosition.institution.save()
        # set again person and position
        # this will set the id of these objects into personPosition.person_id and personPosition.institution_id
        # Looks weird though, should be automatic
        personPosition.person = personPosition.person
        personPosition.institution = personPosition.institution
        personPosition.save()

        if institutionCount % 100 == 0:
            logger.info("Imported %s institutions. Type %s" % (institutionCount, institutionCode))

        institutionCount+=1

    logger.info("Imported %s institutions. Type %s" % (institutionCount, institutionCode))


