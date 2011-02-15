#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, InstitutionNameField, PhoneField, AddressNameField, HouseNumberField, HouseNumberOddField

class CivilParish(models.Model):
    name = InstitutionNameField()
    municipality = InstitutionNameField()

class CivilParishMember(models.Model):
    """ Seniūnas.  A CivilParish member is a regional representative, which helps solve local problems. He usually
    manages a district in a city, or a bigger district out of town"""
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    institution = models.ForeignKey(CivilParish, null=True)
    personalPhone = PhoneField()
    officePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    uniqueKey = models.IntegerField()


class CivilParishStreet(models.Model):
    """ Represents a mapping between a constituency, a district and a street in Lithuania
    """
    institution = models.ForeignKey(CivilParish)
    municipality = AddressNameField(db_index= True)
    civilParish = AddressNameField(db_index = True)
    street = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    numberFrom = HouseNumberField()
    numberTo = HouseNumberField()
    numberOdd = HouseNumberOddField()