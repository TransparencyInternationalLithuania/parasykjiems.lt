#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import AddressNameField

class LithuanianStreetIndexes(models.Model):
    street = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    city_genitive = AddressNameField(db_index = True)
    municipality = AddressNameField(db_index = True)
    # http://en.wikipedia.org/wiki/Elderships_of_Lithuania
    # elderships are sometimes called CivilParish in the code. actually everywhere :)
    civilparish = AddressNameField(db_index = True)


class LithuanianCases(models.Model):
    """ each Lithuanian object can be written in several cases. This mapping helps map from various form
    http://en.wikipedia.org/wiki/List_of_grammatical_cases """

    class Type:
        """ possible types of institution types"""
        Municipality = 1

    nominative = AddressNameField(db_index = True)
    genitive = AddressNameField(db_index = True)
    institutionType = models.IntegerField(db_index = True)


class HierarchicalGeoData(models.Model):
    """ A hierarchical geo data structure. Used to extract data from lithuanian street index page
     http://www.registrucentras.lt/adr/p/index.php?sen_id=5
     """

    class HierarchicalGeoDataType:
        Country = u'Country'
        County = u'County' # Apskritis
        Municipality = u'Municipality'  # Savivaldybė
        CivilParish = u'CivilParish'  # Seniūnija
        City = u'City'
        Street = u'Street'


    # types of hierarchical data. Note that correctness is not enforced programitcally
    # Which means that Country can be put below City, and vice-versa.
    # Import tools must ensure that data is logically insert
    HierarchicalGeoDataTypeChoices = (
        (HierarchicalGeoDataType.Country, u'Country'),
        (HierarchicalGeoDataType.County, u'County'), # Apskritis
        (HierarchicalGeoDataType.Municipality, u'Municipality'), # Savivaldybė
        (HierarchicalGeoDataType.CivilParish, u'Civil parish'), # Seniūnija
        (HierarchicalGeoDataType.City, u'City'),
        (HierarchicalGeoDataType.Street, u'Street'))

    name = models.CharField(max_length = 100)
    name_genitive = models.CharField(max_length = 100, null = True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children", help_text="Parent data, if this is a child node.")
    type = models.CharField(max_length=20, choices=HierarchicalGeoDataTypeChoices)

    @classmethod
    def FindByName(cls, name = None, name_genitive = None, type=None, parentName = None):
        locationInDB = HierarchicalGeoData.objects.all()
        if name is not None:
            locationInDB = locationInDB.filter(name = name)
        if name_genitive is not None:
            locationInDB = locationInDB.filter(name_genitive = name_genitive)

        if (parentName is not None):
            locationInDB = locationInDB.filter(parent__name = parentName)
        if (type is not None):
            locationInDB = locationInDB.filter(type = type)

        try:
            locationInDB = locationInDB[0:1].get()
        except HierarchicalGeoData.DoesNotExist:
            locationInDB = None

        return locationInDB