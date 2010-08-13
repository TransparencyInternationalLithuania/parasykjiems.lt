#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.fields import CharField
from enum import Enum


class PhoneField(CharField):
    description = _("Phone field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 20)
        CharField.__init__(self, *args, **kwargs)

class PersonNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)





class HierarchicalGeoData(models.Model):
    """ A hierarchical geo data structure """


    class HierarchicalGeoDataType:
        Country = 'Country'
        County = 'County' # Apskritis
        Municipality = 'Municipality'  # Savivaldybė
        CivilParish = 'CivilParish'  # Seniūnija
        City = 'City'
        Street = 'Street'
        Seniunaitija = 'Seniunaitija'



    # types of hierarchical data. Note that correctness is not enforced programitcally
    # Which means that Country can be put below City, and vice-versa.
    # Import tools must ensure that data is logically insert
    HierarchicalGeoDataTypeChoices = (
        (HierarchicalGeoDataType.Country, 'Country'),
        (HierarchicalGeoDataType.County, 'County'), # Apskritis
        (HierarchicalGeoDataType.Municipality, 'Municipality'), # Savivaldybė
        (HierarchicalGeoDataType.CivilParish, 'Civil parish'), # Seniūnija
        (HierarchicalGeoDataType.City, 'City'),
        (HierarchicalGeoDataType.Street, 'Street'),
        (HierarchicalGeoDataType.Seniunaitija, 'Seniunaitija')
        )



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
    """
    district = models.CharField(max_length = 100)
    constituency = models.ForeignKey(Constituency)
    street = models.CharField(max_length = 255, db_index = True)
    numberFrom = models.IntegerField(null = True, db_index = True)
    numberTo = models.IntegerField(null = True, db_index = True)
    numberOdd = models.BooleanField()
    city = models.CharField(max_length = 50)
    # should be renamed to polling district
    pollingDistrict = models.CharField(max_length = 100)


class MunicipalityMember(models.Model):
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    email2 = models.EmailField()
    municipality = models.ForeignKey(HierarchicalGeoData, null=True)
    phone = PhoneField()
    phone2 = PhoneField()
    mobilePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    uniqueKey = models.IntegerField()

class SeniunaitijaMember(models.Model):
    """ Seniunaitis. Is accountable to CivilParishMember. Basically he performs any sub-management
    compared to CivilParishMember. One hierarchy level deeper """
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    seniunaitija = models.ForeignKey(HierarchicalGeoData, null=True)
    role = models.CharField(max_length = 20)
    phone = PhoneField()
    homePhone = PhoneField()
    uniqueKey = models.IntegerField()

    
    

class CivilParishMember(models.Model):
    """ Seniūnas.  A CivilParish member is a regional representative, which helps solve local problems. He usually
    manages a district in a city, or a bigger district out of town"""
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    civilParish = models.ForeignKey(HierarchicalGeoData, null=True)
    personalPhone = PhoneField()
    officeEmail = models.EmailField()
    officePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    uniqueKey = models.IntegerField()


class ParliamentMember(models.Model):
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    constituency = models.ForeignKey(Constituency, null=True)
    uniqueKey = models.IntegerField()

    @property
    def fullName(self):
        """returns Name + surname"""
        return self.name + self.surname

    def __unicode__(self):
        return self.fullName
