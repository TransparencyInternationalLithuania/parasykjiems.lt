import logging
import types
from cdb_lt_civilparish.models import CivilParishMember, CivilParishStreet
from cdb_lt_mps.models import ParliamentMember, PollingDistrictStreet
from cdb_lt_municipality.models import Municipality, MunicipalityMember
from cdb_lt_seniunaitija.models import SeniunaitijaMember, SeniunaitijaStreet
from cdb_lt_streets.houseNumberUtils import ifHouseNumberContainLetter, removeLetterFromHouseNumber
import types
from django.db.models.query_utils import Q
from cdb_lt_streets.ltPrefixes import removeGenericPartFromStreet, removeGenericPartFromMunicipality
logger = logging.getLogger(__name__)

def addHouseNumberQuery(query, house_number):
    """ if house number is a numeric, add special conditions to check
    if house number is matched"""
    if house_number is None:
        return query
    if type(house_number) != types.IntType:
        if ifHouseNumberContainLetter(house_number):
            house_number = removeLetterFromHouseNumber(house_number)

        if house_number.isdigit() == False:
            return query

    # convert to integer
        house_number = int(house_number)
    isOdd = house_number % 2

    houseNumberEquals = Q(**{"%s__lte" % "numberFrom": house_number}) & \
        Q(**{"%s__gte" % "numberTo": house_number}) & \
        Q(**{"%s" % "numberOdd": isOdd})

    houseNumberEualsFrom = Q(**{"%s" % "numberFrom": house_number})
    houseNumberEualsTo = Q(**{"%s" % "numberTo": house_number})

    houseNumberIsNull = Q(**{"%s__isnull" % "numberFrom": True}) & \
        Q(**{"%s__isnull" % "numberTo": True})

    orQuery = houseNumberEquals | houseNumberIsNull | houseNumberEualsFrom | houseNumberEualsTo

    query = query.filter(orQuery)
    return query

def findMPs(municipality = None, city = None, street = None, house_number = None,  *args, **kwargs):
    #street = removeGenericPartFromStreet(street)
    #municipality = removeGenericPartFromMunicipality(municipality)

    logging.info("searching for MP: street %s, city %s, municipality %s" % (street, city, municipality))


    idList = findLT_street_index_id(PollingDistrictStreet, municipality=municipality, city=city,  street=street, house_number=house_number)
    #idList = findLT_MPs_Id(municipality=municipality, city=city,  city_gen= city_gen, street=street, house_number=house_number)

    logging.debug("found MPs in following constituency : %s" % (idList))
    members = ParliamentMember.objects.all().filter(institution__in = idList)
    return members

def findMunicipalityMembers(municipality = None, city = None, street = None, house_number = None, *args, **kwargs):

    try:
        query = Municipality.objects.all().filter(name__contains = municipality)

        query = query.distinct() \
            .values('id')
        idList = [p['id'] for p in query]
    except Municipality.DoesNotExist:
        logging.info("no municipalities found")
        return []

    members = MunicipalityMember.objects.all().filter(institution__in = idList)
    return members

def extractInstitutionColumIds(query):
    institutionColumName = "institution"
    query = query.distinct() \
            .values(institutionColumName)
    idList = [p[institutionColumName] for p in query]
    return idList


def getCityQuery(city = None, operator="__icontains"):
    cityQuery = None
    if city is not None:
        cityQuery = Q(**{"city%s" % operator : city})
    return cityQuery

def searchPartial(streetQuery = None, **kwargs):
    modelToSearchIn = kwargs['modelToSearchIn']
    municipality = kwargs['municipality']
    city = kwargs['city']
    city_gen = kwargs['city_gen']
    street = kwargs['street']
    house_number = kwargs['house_number']

    cityQuery = getCityQuery(city=city, city_gen= city_gen)
    # first search by street without house number
    try:
        query = modelToSearchIn.objects.all().filter(municipality__icontains = municipality)\
            .filter(streetQuery) \
            .filter(cityQuery)
        streetIdList = extractInstitutionColumIds(query)
        if len(streetIdList) > 0:
            if len(streetIdList) == 1:
                #print "found following ids %s" % streetIdList
                return streetIdList

            # we have found more than 1 member.  Try to search with street number to narrow
            query = modelToSearchIn.objects.all().filter(municipality__icontains = municipality)\
                .filter(streetQuery) \
                .filter(cityQuery)
            query = addHouseNumberQuery(query, house_number)
            #print query.query

            streetNumberIdList = extractInstitutionColumIds(query)
            if len(streetNumberIdList) > 0:
                #print "found following ids %s" % streetNumberIdList
                return streetNumberIdList
            else:
                #print "found following ids %s" % streetIdList
                return streetIdList

    except modelToSearchIn.DoesNotExist:
        pass
    return []

def findLT_street_index_id(modelToSearchIn, municipality = None, city = None, street = None, house_number = None):
    """ At the moment territory data for each representative is stored in separate table.
    This query searches some table (objectToSearchIn) for instituions pointed by an address.

    All representative searches will be done through this method"""


    logger.info("Will search for representatives in object: %s" % modelToSearchIn.objects.model._meta.object_name)



    municipalityQuery = Q(**{"municipality" : municipality})
    # search without street. Will return tens of results, but it is better than nothing
    cityQuery = Q(**{"city" : city})
    list = searchPartialCity(modelToSearchIn= modelToSearchIn, municipalityQuery=municipalityQuery, cityQuery=cityQuery)
    if len(list) > 0:
        return list

    logger.debug("Did not find any ids")
    return []

def searchPartialCity(modelToSearchIn, municipalityQuery = None, cityQuery = None):
    try:
        query = modelToSearchIn.objects.all().filter(municipalityQuery)\
            .filter(cityQuery)
        #print query.query

        idList = extractInstitutionColumIds(query)
        return idList
    except modelToSearchIn.DoesNotExist:
        pass
    return []


def findCivilParishMembers(municipality = None, city = None, street = None, house_number = None,  *args, **kwargs):
    #street = removeGenericPartFromStreet(street)
    #municipality = removeGenericPartFromMunicipality(municipality)

    idList = findLT_street_index_id(modelToSearchIn=CivilParishStreet, municipality=municipality, city=city,  street=street, house_number=house_number)

    members = CivilParishMember.objects.all().filter(institution__in = idList)
    return members

def findSeniunaitijaMembers(municipality = None, city = None, street = None, house_number = None, *args, **kwargs):
    #street = removeGenericPartFromStreet(street)
    #municipality = removeGenericPartFromMunicipality(municipality)

    # since in Lithuania it is the primary key to identify cities
    idList = findLT_street_index_id(SeniunaitijaStreet, municipality=municipality, street= street, house_number= house_number)
    members = SeniunaitijaMember.objects.all().filter(institution__in = idList)
    return members
