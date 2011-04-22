#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from settings import *
from territories.models import InstitutionTerritory
from territories.searchMembers import findInstitutionTerritories

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSearchCivilParishStreets_SingleStreet(TestCase):
    fixtures = ['InstitutionIndexes/kaimas.json',
                'InstitutionIndexes/institutions_single_typed.json']

    def setUp(self):
        pass

    def testSearch(self):
        municipality = u"Alytaus rajono savivaldybė"
        city=u"Aniškio kaimas"
        street=None
        house_number=None
        ids = findInstitutionTerritories(municipality=municipality, city=city,  street=street, house_number=house_number)
        self.assertEquals([1], ids)

class TestSearchInstitutionStreets_WithStreetAndHouseNumber(TestCase):
    fixtures = ['InstitutionIndexes/several Gedimino 9, Vilnius MPs.json',
                'InstitutionIndexes/institutions_single_typed.json']

    municipality = u"Vilniaus miesto savivaldybė"
    city=u"Vilniaus miestas"
    street= u"Gedimino prospektas"

    def setUp(self):
        pass

    def testSearchOdd(self):
        """ we have two rows, but we need to find only the match with even house number"""
        house_number=9
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1], ids)

    def testSearch_Out_of_street_range(self):
        """ In case there are defined ranges for house numbers, but the provided house range is out of range, just return results for whole street"""
        house_number=14
        all = list(InstitutionTerritory.objects.all())
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1, 2], ids)

    def testSearch_DoNotIgnoreStreetpart(self):
        """ In case there are defined ranges for house numbers, but the provided house range is out of range, just return results for whole street.
        If our code would ignore street part, the result would be [2,4] not [2]"""

        house_number=10
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([2], ids)

    def testSearchWhereStreetNumberHasNoRange(self):
        """ Sometimes individual houses will be listed, in that case query must be a bit different """
        house_number = 10
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=u"Betkokia gatvė", house_number=house_number)
        self.assertEquals([3], ids)

    def testSearch_Multiple_Results_ForDStreet(self):
        """ Single streets has more than one representative, but house number is not given  """
        house_number = None
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1,2], ids)

    def testSearchHouseWithNumber(self):
        """ In DB we have a street with range 9 to 13, but we are searching for 11A.  This range should be included, even if it hass letter"""
        house_number=u"11A"
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=self.street, house_number=house_number)
        self.assertEquals([1], ids)



class TestSearchInstitutionStreets_SingleRepresentative(TestCase):
    fixtures = ['InstitutionIndexes/single representative in street.json',
                'InstitutionIndexes/institutions_single_typed.json']

    municipality = u"Vilniaus miesto savivaldybė"
    city=u"Vilniaus miestas"
    street= u"Gedimino prospektas"

    def setUp(self):
        pass

    def testSearchSingleStreet(self):
        """ There are two streets by different name, find the correct one"""
        ids = findInstitutionTerritories(municipality=self.municipality, city=self.city,  street=self.street)
        self.assertEquals([1], ids)

class TestSearchInstitutionStreets_ArminuKaimas(TestCase):
    fixtures = ['InstitutionIndexes/arminu i kaimas.json',
                'InstitutionIndexes/institutions_single_typed.json'
                ]

    def setUp(self):
        pass

    def testSearchWhenStreetIsNOne(self):
        """ Two cities with same name exists, but they differ only by civil parish. Return both cities"""
        ids = findInstitutionTerritories(municipality=u"Alytaus rajono savivaldybė", city=u"Arminų I kaimas",  street=None)
        self.assertEquals([1, 2], ids)

    def testSearchWhenStreetIsNOne(self):
        """ Two cities with same name exists, but they differ only by civil parish.
        Return specific city"""
        ids = findInstitutionTerritories(municipality=u"Alytaus rajono savivaldybė", civilParish=u"Krokialaukio seniūnija", city=u"Arminų I kaimas",  street=None)
        self.assertEquals([2], ids)

class TestSearchInstitutionStreets_NumberToIsNone(TestCase):
    fixtures = ['InstitutionIndexes/number To is None.json',
                'InstitutionIndexes/institutions_single_typed.json']

    def setUp(self):
        pass

    def testSearchNumberToIsNone(self):
        """ Data contains exact house value: numberFrom is give, numberTo is None.
        Query should consider that numberTo might be None, but not necesarrily"""
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number=9)
        self.assertEquals([1], ids)

    def testNumberContainsFlatNumber(self):
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number="9-5")
        self.assertEquals([1], ids)

class TestSearchInstitutionStreets_NumberWithLetter(TestCase):
    fixtures = ['InstitutionIndexes/number with letter.json',
                'InstitutionIndexes/institutions_single_typed.json']

    def setUp(self):
        pass

    def testSearchNumberWithLetter(self):
        """ Data contains exact house value: numberFrom is give, numberTo is None.
        Query should consider that numberTo might be None, but not necesarrily"""
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number=9)
        self.assertEquals([2], ids)

        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number="9A")
        self.assertEquals([1], ids)

    def testSearchNumberWithLetter_Letter_is_in_another_house_range(self):
        """ One street from 10 to 20, another street 14a    Should find correctly one or another"""
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Vaižganto gatvė", house_number="56")
        self.assertEquals([3], ids)

        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Vaižganto gatvė", house_number="56A")
        self.assertEquals([4], ids)

    def testSearchNumberWithLetter_Letter_is_lowercaes(self):
        """ All house numbers if contains letter, data must be in uppercase. However, if we query with lowercase, still find it """
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Vaižganto gatvė", house_number="56a")
        self.assertEquals([4], ids)

class TestSearchInstitutionStreets_DifferentTypesOfInstitutions(TestCase):
    fixtures = ['InstitutionIndexes/multipleInstitutionTypes/Two institution types_mp_and_mayor.json']

    def setUp(self):
        pass

    def testSearchMPandMayor(self):
        """ Different types of institutions might have different territory information. For example mayors
        only rely on municipality, but MPs are searched down to the street and house number.

        Ensure that both institutions are returned"""

        # returns only [1] for now, but should return both institution ids
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number=9)
        self.assertEquals([1, 2], ids)

class TestSearchInstitutionStreets_DifferentTypesOfInstitutionsMPAndMayor(TestCase):
    fixtures = ['InstitutionIndexes/multipleInstitutionTypes/Two institution types_mp_and_civilParish.json']

    def setUp(self):
        pass

    def testSearchMPAndCivilParish(self):
        """ Different types of institutions might have different territory information. For example mayors
        only rely on municipality, but MPs are searched down to the street and house number.

        Ensure that both institutions are returned"""

        # returns only [1] for now, but should return both institution ids
        ids = findInstitutionTerritories(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilniaus miestas",  street=u"Gedimino prospektas", house_number=9)
        self.assertEquals([1, 2], ids)

class TestSearchInstitutionStreets_IssuesWithCivilParish(TestCase):
    fixtures = ['InstitutionIndexes/issuesWithCivilParish/MPandCivParinstitution.json',
                'InstitutionIndexes/issuesWithCivilParish/singleCivilParishAndMp.json']

    def setUp(self):
        pass

    def testSearchMPAndCivilParish(self):
        """ MP institution has territory without civilParish,  but civil parish institution has a civil parish name set.
        Must return both in this case"""

        # returns only [1] for now, but should return both institution ids
        all = list(InstitutionTerritory.objects.all())
        ids = findInstitutionTerritories(municipality=u"Kazlų Rūdos savivaldybė", civilParish=u"Jankų seniūnija", city=u"Jankų kaimas",  street=u"")
        self.assertEquals([2, 1], ids)

class TestSearchInstitutionStreets_IssuesWithCivilParish_MultipleCivPar(TestCase):
    fixtures = ['InstitutionIndexes/issuesWithCivilParish/MPandCivParinstitution.json',
                'InstitutionIndexes/issuesWithCivilParish/multipleCivilParishAndMp.json']

    def setUp(self):
        pass

    def testSearchMPAndCivilParish(self):
        """ MP institution has territory without civilParish,  but civil parish institution has a civil parish name set.
        Also exists a third institution with civl parish - seniunaitija. Must return all 3"""

        # returns only [1] for now, but should return both institution ids
        all = list(InstitutionTerritory.objects.all())
        ids = findInstitutionTerritories(municipality=u"Kazlų Rūdos savivaldybė", civilParish=u"Jankų seniūnija", city=u"Jankų kaimas",  street=u"")
        self.assertEquals([2, 3, 1], ids)

class TestSearchInstitutionStreets_StreetNamesWithDots(TestCase):
    fixtures = ['InstitutionIndexes/streetNamesWithDots/streetNameWithDots.json']

    def setUp(self):
        pass

    def testSearchMPAndCivilParish(self):
        """Some streets in our address db are with dots, for example
        I. Šimulionio gatvė.

        If user queries with 'Igno Šimulionio gatvė', then we should still find this street, but not others"""

        # returns only [1] for now, but should return both institution ids
        all = list(InstitutionTerritory.objects.all())
        ids = findInstitutionTerritories(municipality=u"Kazlų Rūdos savivaldybė", civilParish=u"Jankų seniūnija", city=u"Jankų kaimas",  street=u"Igno Šimulionio")
        self.assertEquals([1], ids)


