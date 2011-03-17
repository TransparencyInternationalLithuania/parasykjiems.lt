import logging
import types
import types
from django.db.models.query_utils import Q
from contactdb.models import PersonPosition
from territories.houseNumberUtils import isHouseNumberOdd, ifHouseNumberContainLetter, padHouseNumberWithZeroes
from territories.models import InstitutionTerritory

logger = logging.getLogger(__name__)

def addHouseNumberQuery2(query, house_number):
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

def getHouseNumberQuery(house_number = None):
    if house_number is None:
        return query

    isOdd = isHouseNumberOdd(house_number)
    isLetter = ifHouseNumberContainLetter(house_number)
    house_number = padHouseNumberWithZeroes(house_number)

    houseNumberEualsFrom = Q(**{"%s" % "numberFrom": house_number}) & Q(**{"%s" % "numberTo": u""})

    if isLetter:
        return houseNumberEualsFrom

    houseNumberInRange = Q(**{"%s__lte" % "numberFrom": house_number}) & \
        Q(**{"%s__gte" % "numberTo": house_number}) & \
        Q(**{"%s" % "numberOdd": isOdd})

    orQuery = houseNumberInRange | houseNumberEualsFrom  # | houseNumberIsNull | houseNumberEualsFrom | houseNumberEualsTo
    return orQuery


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

def findInstitutionTerritories(municipality = None, civilParish = None, city = None, street = None, house_number = None):
    """ At the moment territory data for each representative is stored in separate table.
    This query searches some table (objectToSearchIn) for instituions pointed by an address.

    House_number can either be integer, or a string in case the house number has a letter. Do not pad house number with zeroes.

    All representative searches will be done through this method"""

    if civilParish is None:
        civilParish = u""
    civilParish = civilParish.strip()

    if street is None:
        street = u""
    street = street.strip()

    #logger.info("Will search for representatives in object: %s" % modelToSearchIn.objects.model._meta.object_name)

    municipalityQuery = Q(**{"municipality" : municipality})
    # search without street. Might return more results, if there is a street number in the data
    cityQuery = Q(**{"city" : city})
    cityList = searchPartialCity(queries=[municipalityQuery, cityQuery])
    if len(cityList) < 2:
        return cityList


    # try searchign with civilParish if it is not None
    if civilParish != u"":
        civilparishQuery = Q(**{"civilParish": civilParish})
        civilParishList = searchPartialCity(queries=[municipalityQuery, civilparishQuery, cityQuery])

        if len(civilParishList) == 0:
            return cityList

        if len(civilParishList) == 1:
            return civilParishList

        # if we have more than one result, replace city list with our result
        if len(civilParishList) > 0:
            cityList = civilParishList




    # if street is empty or None, just return what we have
    if type(street) != types.UnicodeType:
        raise UnicodeError("street was not given in unicode")
    if street == u"":
       return cityList

    # search with street
    streetQuery = Q(**{"street" : street})
    streetList = searchPartialCity(queries=[municipalityQuery, cityQuery, streetQuery])
    if len(streetList) < 2:
        return streetList

    # in case we do not have number, return all we have
    if house_number is None or house_number == u"":
        return streetList

    # we have got more than two rows. So now search with house number
    numberQuery = getHouseNumberQuery(house_number)
    #print buildFinalQuery(modelToSearchIn= modelToSearchIn, queries=[municipalityQuery, cityQuery, numberQuery]).query

    houseList = searchPartialCity(queries=[municipalityQuery, cityQuery, streetQuery, numberQuery], doPrint=False)

    if len(houseList) > 0:
        return houseList
    return streetList

def buildFinalQuery(queries):
    query = InstitutionTerritory.objects.all()
    for q in queries:
        query = query.filter(q)
    return query

def searchPartialCity(queries, doPrint = False):
    try:
        query = buildFinalQuery(queries)
        if doPrint:
            strQuery = str(query.query)
            strQuery = strQuery.encode("utf_8")
            print strQuery
        idList = extractInstitutionColumIds(query)
        return idList
    except InstitutionTerritory.DoesNotExist:
        pass
    return []


def findPersonPositions(municipality = None, civilParish = None,city = None, street = None, house_number = None,  *args, **kwargs):
    idList = findInstitutionTerritories(municipality=municipality, civilParish = civilParish, city=city,  street=street, house_number=house_number)

    
    members = PersonPosition.objects.all().filter(institution__in = idList)
    return members

