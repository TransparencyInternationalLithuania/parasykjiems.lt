#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class HierarchicalGeoData(models.Model):
    """ A hierarchical geo data structure """


    # types of hierarchical data. Note that correctness is not enforced programitcally
    # Which means that Country can be put below City, and vice-versa.
    # Import tools must ensure that data is logically insert
    HierarchicalGeoDataType = (
        ('Country', 'Country'),
        ('County', 'County'), # Apskritis
        ('Municipality', 'Municipality'), # Savivaldybė
        ('CivilParish', 'Civil parish'), # Seniūnija
        ('City', 'City'),
        ('Street', 'Street')
    )



    name = models.CharField(max_length = 100)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children", help_text="Parent data, if this is a child node.")
    type = models.CharField(max_length=20, choices=HierarchicalGeoDataType)

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

    



class Constituency(models.Model):
    """ Contains counties, for example:
     Constituency: Danės rinkimų apygarda Nr. 19
     Baltijos rinkimų apygarda Nr. 20
     Kauno Kėinių rinkimų apygarda Nr. 65
     etc
     """
    name = models.CharField(max_length = 100)
    nr = models.IntegerField()

    def ToString(self):
        return self.__unicode__()

    def __unicode__(self):
        if (self.nr is None):
            number = 0
        else:
            number = self.nr
        
        return "Constituency: %s , nr: %d" % (self.name, number)



class PollingDistrictStreet(models.Model):
    """ Represents a mapping between a constituency, a district and a street in Lithuania
    TODO rename to PollingDistrictStreet
    """
    district = models.CharField(max_length = 100)
    constituency = models.ForeignKey(Constituency)
    street = models.CharField(max_length = 255)
    city = models.CharField(max_length = 50)
    # should be renamed to polling district
    electionDistrict = models.CharField(max_length = 100)
    

class CivilParishMember(models.Model):
    """ Seniūnas.  A CivilParish member is a regional representative, which helps solve local problems. He usually
    manages a district in a city, or a bigger district out of town"""
    name = models.CharField(max_length = 50)
    surname = models.CharField(max_length = 50)
    email = models.CharField(max_length = 100)
    civilParish = models.ForeignKey(HierarchicalGeoData, null=True)
    personalPhone = models.CharField(max_length = 20)
    officeEmail = models.EmailField()
    officePhone = models.CharField(max_length = 20)
    officeAddress = models.CharField(max_length = 100)


class ParliamentMember(models.Model):
    name = models.CharField(max_length = 50)
    surname = models.CharField(max_length = 50)
    email = models.CharField(max_length = 100)
    constituency = models.ForeignKey(Constituency)

    @property
    def fullName(self):
        """returns Name + surname"""
        return self.name + self.surname

    def __unicode__(self):
        return self.fullName
