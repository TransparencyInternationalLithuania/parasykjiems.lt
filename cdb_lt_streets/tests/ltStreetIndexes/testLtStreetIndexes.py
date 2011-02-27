#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from cdb_lt_streets.searchInIndex import searchInIndex
from settings import *

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSearchLtStreetIndex_SingleStreet(TestCase):
    fixtures = ['ltstreetindexes/several ordinary streets.json',
                'ltstreetindexes/LithuanianMunicipalityCases.json']

    def setUp(self):
        pass

    def testSearchCity_GentiveForm(self):
        """ City can be in two forms. such as Vilnius and 'Vilniaus miestas'. The latter is the genitive form"""
        municipality = u""  # will match Kauno
        city=u"Kauno"
        addresses = searchInIndex(municipality=municipality, city=city)

        ids = [a.id for a in addresses]
        self.assertEquals([3], ids)

    def testSearchMunicipality_GenitiveForm(self):
        """ Municiaplity can be in two froms, such as "Rokiškis" and "Roškio rajono savivaldybė". """
        municipality = u"Vilnius" 
        city=u""
        addresses = searchInIndex(municipality=municipality, city=city)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)

    def testSearchMunicipalityNotExact(self):
        """ municipality is not exact, but possible enough to guess a result. need contains query"""
        municipality = u"auno"  # will match Kauno
        city=u""
        addresses = searchInIndex(municipality=municipality, city=city)

        ids = [a.id for a in addresses]
        self.assertEquals([3], ids)

    def testSearchWithCity(self):
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        addresses = searchInIndex(municipality=municipality, city=city)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)
        self.assertEquals(2, len(addresses))

    def testSearch_StreetWith_LithuanianLetters(self):
        """ It appears that, at least for sqlite, a and A are the same letters when doing icontains, but not for
        national letters, such as ž and Ž"""
        municipality = u""
        city=u""
        street= u"žygio"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([4], ids)

    def testSearch_CityWith_LithuanianLetters(self):
        """ It appears that, at least for sqlite, a and A are the same letters when doing icontains, but not for
        national letters, such as ž and Ž"""
        municipality = u""
        city=u"žiežmariai"
        street= u""
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([4], ids)

    def testSearch_MunicipalityWith_LithuanianLetters(self):
        """ It appears that, at least for sqlite, a and A are the same letters when doing icontains, but not for
        national letters, such as ž and Ž"""
        municipality = u"žiežmarių"
        city=u""
        street= u""
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([4], ids)

    def testSearchWithStreet(self):
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        street= u"Gedimino prospektas"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(1, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearch_CityMustBeLike(self):
        """ query for city must be like, not exactly equals, since this will ignore case"""
        # note that city is lowercase
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"vilnius"
        street= u"Gedimino prospektas"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(1, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearchWithStreet_Without_municipality(self):
        """ do not fail if municipality is empty and street is empty"""
        municipality = u""
        city=u"Kaunas"
        street= u""
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(3, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearchWithStreet_Without_municipality_2(self):
        """ do not fail if municipality is empty and street is not empty"""
        # street is exactly equal
        municipality = u""
        city=u"Kaunas"
        street= u"palemono gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(3, addresses[0].id)
        self.assertEquals(1, len(addresses))

    def testSearchWithStreet_Street_not_exactly_equal(self):
        """ street is not exactly equal. Do a like query"""
        municipality = u""
        city=u"Kaunas"
        street= u"palemon"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        self.assertEquals(3, addresses[0].id)
        self.assertEquals(1, len(addresses))


    def testSearchWithStreet_No_street_ending(self):
        """ street does not have an ending"""
        municipality = u""
        city=u"random"
        street= u"keksto 19"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([], ids)

    def testMunicipalityShortForm(self):
        """ Municipalities can be shortened, or long form. for example.
        Vilniaus m. sav
        Vilniaus miesto savivaldybė"""
        municipality = u"Vilniaus m. sav."
        city=u"Vilniaus miestas"
        street= u"Gedimino prospektas"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)


class TestSearchLtStreetIndex_StreetsWithNumbersInName(TestCase):
    fixtures = ['ltstreetindexes/streets with numbers in name.default.json']

    def setUp(self):
        pass

    def testSearch_RemoveStreetEnding(self):
        """ Street name is correct, but in the middle there should be numbers. So strip the last part from street
        The test fails, since the street is actually
        Antavilių sodų 1-oji gatvė
        Antavilių sodų 2-oji gatvė"""
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        street= u"Antavilių sodų gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)
        self.assertEquals(2, len(addresses))

    def testSearch_MoreThanOneResult_DoNotFailIfMuniciaplityIsEmpty(self):
        """ Remove street ending, municipality is empty"""
        municipality = u""
        city=u"Vilnius"
        street= u"Antavilių sodų gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([1, 2], ids)
        self.assertEquals(2, len(addresses))

    def testSearch_StreetIsNotExact_Needs_istartsWith(self):
        """ Street name is not exact, and exactly startswith query"""
        municipality = u"Vilniaus miesto savivaldybė"
        city=u"Vilnius"
        street= u"Sodų gatvė"
        addresses = searchInIndex(municipality=municipality, city=city,  street=street)

        ids = [a.id for a in addresses]
        self.assertEquals([3], ids)
        self.assertEquals(1, len(addresses))


class TestSearchLtStreetIndex_DifferentEndings(TestCase):
    fixtures = ['ltstreetindexes/different street endings.default.json']

    def setUp(self):
        pass

    def testSearch_ExactNameAndExactStreet_ending(self):
        """ Street name is correct, and also street ending matches the result.
        Do not strip street ending."""
        addresses = searchInIndex(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilnius",  street=u"Gedimino prospektas")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)

    def testSearch_ConvertEndingToLongForm(self):
        # convert street ending from short to long form
        addresses = searchInIndex(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilnius",  street=u"Gedimino pr.")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)

    def testSearch_Search_By_Street_ending_form(self):
        # convert street ending from short to long form
        addresses = searchInIndex(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilnius",  street=u"Gedimino g.")
        ids = [a.id for a in addresses]
        self.assertEquals([2], ids)

class TestSearchLtStreetIndex_StreetDoubleWordAndLithuanianLetter(TestCase):
    fixtures = ['ltstreetindexes/Double letter lithuanian.json']

    def setUp(self):
        pass

    def testSearch_ExactNameAndExactStreet_ending(self):
        """ Street is correct, data is correct. But we should not remove uppercase letters, since this is important.
        For example, sqlite does treat lowercase lithuanian letters the same as uppercase, so this must be correct"""
        addresses = searchInIndex(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilnius",  street=u"J. Žemgulio gatvė")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)

    def testSearch_FindAddress_With_street_Even_If_Data_does_not_contain_street(self):
        """ Sometimes user will enter street name. however, the data might not contain any streets, only city,
        municipality. So if queries with street fail, search without """

        # we will have one address in Vilnius city, even though some unknown street will know exist
        addresses = searchInIndex(municipality=u"Vilniaus miesto savivaldybė", city=u"Vilnius",  street=u"some unknown gatvė")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)


class TestSearchLtStreetIndex_Village(TestCase):
    fixtures = ['ltstreetindexes/village.json']

    def setUp(self):
        pass

    def testSearch_city_short_ending(self):
        """ Miroslavo k. and Miroslavo kaimas is the same.
        Allow searching it by both forms, i.e. by short and long city form"""

        addresses = searchInIndex(municipality=u"Alytaus rajono savivaldybė", city=u"Miroslavo k.",  street=u"")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)

    def testSearch_Municipality_can_be_either_two_or_one_word(self):
        """ Vilniaus savivaldybė and Vilniaus miesto savivaldybė and Vilniaus m. savivaldybė
        Allow searching it by both forms, i.e. by shorter and long form"""

        addresses = searchInIndex(municipality=u"Alytaus savivaldybė", city=u"Miroslavo kaimas",  street=u"")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)

        addresses = searchInIndex(municipality=u"Alytaus r. savivaldybė", city=u"Miroslavo kaimas",  street=u"")
        ids = [a.id for a in addresses]
        self.assertEquals([1], ids)