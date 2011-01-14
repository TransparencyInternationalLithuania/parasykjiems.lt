#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, InstitutionNameField, PhoneField, AddressNameField

class CivilParish(models.Model):
    name = InstitutionNameField()
    municipality = InstitutionNameField()

class CivilParishMember(models.Model):
    """ Seniūnas.  A CivilParish member is a regional representative, which helps solve local problems. He usually
    manages a district in a city, or a bigger district out of town"""
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    civilParish = models.ForeignKey(CivilParish, null=True)
    personalPhone = PhoneField()
    officePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    uniqueKey = models.IntegerField()


class CivilParishStreet(models.Model):
    """ Represents a mapping between a constituency, a district and a street in Lithuania
    """
    civilParish = models.ForeignKey(CivilParish)
    municipality = AddressNameField()
    street = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    city_genitive = AddressNameField(db_index = True)
    numberFrom = models.CharField(max_length=4, null = True, db_index = True)
    numberTo = models.CharField(max_length=4, null = True, db_index = True)
    numberOdd = models.BooleanField(db_index = True)