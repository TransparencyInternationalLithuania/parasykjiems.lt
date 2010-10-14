#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
class HierarchicalGeoData(models.Model):
    """ A hierarchical geo data structure """

    class HierarchicalGeoDataType:
        Country = 'Country'
        County = 'County' # Apskritis
        Municipality = 'Municipality'  # Savivaldybė
        CivilParish = 'CivilParish'  # Seniūnija
        City = 'City'
        Street = 'Street'


    # types of hierarchical data. Note that correctness is not enforced programitcally
    # Which means that Country can be put below City, and vice-versa.
    # Import tools must ensure that data is logically insert
    HierarchicalGeoDataTypeChoices = (
        (HierarchicalGeoDataType.Country, 'Country'),
        (HierarchicalGeoDataType.County, 'County'), # Apskritis
        (HierarchicalGeoDataType.Municipality, 'Municipality'), # Savivaldybė
        (HierarchicalGeoDataType.CivilParish, 'Civil parish'), # Seniūnija
        (HierarchicalGeoDataType.City, 'City'),
        (HierarchicalGeoDataType.Street, 'Street'))

    name = models.CharField(max_length = 100)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children", help_text="Parent data, if this is a child node.")
    type = models.CharField(max_length=20, choices=HierarchicalGeoDataTypeChoices)

    @classmethod
    def FindByName(cls, name, type=None, parentName = None):
        locationInDB = HierarchicalGeoData.objects.filter(name = name)
        if (parentName is not None):
            locationInDB = locationInDB.filter(parent__name = parentName)
        if (type is not None):
            locationInDB = locationInDB.filter(type = type)

        try:
            locationInDB = locationInDB[0:1].get()
        except HierarchicalGeoData.DoesNotExist:
            locationInDB = None

        return locationInDB