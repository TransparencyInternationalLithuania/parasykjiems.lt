#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import types
import types
from django.db.models.query_utils import Q
from contactdb.models import PersonPosition
from territories.houseNumberUtils import isHouseNumberOdd, ifHouseNumberContainLetter, padHouseNumberWithZeroes, removeFlatNumber
from territories.models import InstitutionTerritory
from cdb_lt.management.commands.createMembers import InstitutionMunicipalityCode
from territories.streetUtils import changeDoubleWordStreetToDot

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

    house_number = removeFlatNumber(house_number)
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

institutionColumName = "institution"
institutionTypeColumName = "institution__institutionType__code"
def extractInstitutionColumIds(query):
    query = query.distinct() \
            .values(institutionColumName, institutionTypeColumName)
    q = list(query)
    return q
    #idList = [p[institutionColumName] for p in query]
    #return idList


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

def selectivelyReturnResults(*args):
    institutionTypesServed = {}
    results = []
    for resultSet in args:
        currentTypes = dict(institutionTypesServed)
        for territory in resultSet:
            institutionType = territory[institutionTypeColumName]
            if currentTypes.has_key(institutionType):
                continue
            institutionTypesServed[institutionType] = institutionType
            #institutionId = territory[institutionColumName]
            results.append(territory)
    return results

def findInstitutionTerritories(municipality = None, civilParish = None, city = None, street = None, house_number = None):
    results = findInstitutionTerritoriesWithTypes(municipality = municipality, civilParish = civilParish, city = city, street = street, house_number = house_number)
    ter = [t[institutionColumName] for t in results]
    return ter

def findInstitutionTerritoriesWithTypes(municipality = None, civilParish = None, city = None, street = None, house_number = None):
    """ InstitutionTerritory is stored in single table.  We will try separate queries to narrow down results.
    note that some institution territory data might be more detailed than the others, so we will have
    to selectively filter the results by institution type when returning results.

    House_number can either be integer, or a string in case the house number has a letter. Do not pad house number with zeroes.

    All representative searches will be done through this method"""

    if civilParish is None:
        civilParish = u""
    civilParish = civilParish.strip()

    if street is None:
        street = u""
    street = street.strip()

    #logger.info("Will search for representatives in object: %s" % modelToSearchIn.objects.model._meta.object_name)




    # search for municipality
    # do a special query, limiting to only specific institution Type
    municipalityQuery = Q(**{"municipality" : municipality})
    municipalityQueryType = Q(**{"institution__institutionType__code" : InstitutionMunicipalityCode})
    municipalityList = searchPartialCity(queries=[municipalityQuery, municipalityQueryType])
    
    # search without street. Might return more results, if there is a street number in the data
    cityQuery = Q(**{"city" : city})
    cityList = searchPartialCity(queries=[municipalityQuery, cityQuery])
    if len(cityList) < 2:
        return selectivelyReturnResults(cityList, municipalityList)


    # try searching with civilParish if it is not None
    if civilParish != u"" and street == u"":
        civilparishQuery = Q(**{"civilParish": civilParish})
        civilParishList = searchPartialCity(queries=[municipalityQuery, civilparishQuery, cityQuery])

        if len(civilParishList) == 0:
            return selectivelyReturnResults(cityList, municipalityList)

        if len(civilParishList) == 1:
            return selectivelyReturnResults(civilParishList, cityList, municipalityList)

        """# if we have more than one result, replace city list with our result
        if len(civilParishList) > 0:
            cityList = civilParishList"""




    # if street is empty or None, just return what we have
    if type(street) != types.UnicodeType:
        raise UnicodeError("street was not given in unicode")
    if street == u"":
       return selectivelyReturnResults(civilParishList, cityList, municipalityList)

    # search with street
    # convert street from "Igno Šimulionio gatvė" to "Šimulionio gatvė", since in DB we have only "I. Šimulionio gatvė"
    # also search with __contains in this case
    street = changeDoubleWordStreetToDot(street)
    streetQuery = Q(**{"street__contains" : street})
    streetList = searchPartialCity(queries=[municipalityQuery, cityQuery, streetQuery])
    if len(streetList) < 2:
        return selectivelyReturnResults(streetList, cityList, municipalityList)

    # in case we do not have number, return all we have
    if house_number is None or house_number == u"":
        return selectivelyReturnResults(municipalityList, streetList, cityList)

    # we have got more than two rows. So now search with house number
    numberQuery = getHouseNumberQuery(house_number)
    #print buildFinalQuery(modelToSearchIn= modelToSearchIn, queries=[municipalityQuery, cityQuery, numberQuery]).query

    houseList = searchPartialCity(queries=[municipalityQuery, cityQuery, streetQuery, numberQuery], doPrint=False)

    if len(houseList) > 0:
        return selectivelyReturnResults(houseList, streetList, cityList, municipalityList)
    return selectivelyReturnResults(streetList, cityList, municipalityList)

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



