#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.query_utils import Q
from pjutils.uniconsole import *

class HierarchicalGeoData(models.Model):
    """ A hierarchical geo data structure. Used to extract data from lithuanian street index page
     http://www.registrucentras.lt/adr/p/index.php?sen_id=5
     """

    class HierarchicalGeoDataType:
        Country = u'country'
        County = u'county' # Apskritis
        Municipality = u'municipality'  # Savivaldybė
        CivilParish = u'civilparish'  # Seniūnija
        City = u'city'
        Street = u'street'


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
    def FindByName(cls, name = None, name_genitive = None, type=None, parentName = None, parentNameGenitive = None):
        locationInDB = HierarchicalGeoData.objects.all()
        if name is not None:
            locationInDB = locationInDB.filter(name = name)
        if name_genitive is not None:
            locationInDB = locationInDB.filter(name_genitive = name_genitive)

        if parentName is not None:
            locationInDB = locationInDB.filter(parent__name = parentName)
        if parentNameGenitive is not None:
            cityQuery_Nominative = Q(**{"parent__name": parentNameGenitive})
            #cityQuery_Genitive = Q(**{"parent__parent__name": parentParentNameGenitive})
            #cityQuery = cityQuery_Genitive | cityQuery_Nominative
            locationInDB = locationInDB.filter(cityQuery_Nominative)
        if type is not None:
            locationInDB = locationInDB.filter(type = type)


        try:
            locationInDB = locationInDB[0:1].get()
        except HierarchicalGeoData.DoesNotExist:
            locationInDB = None

        return locationInDB