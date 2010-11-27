#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, PhoneField, InstitutionNameField, AddressNameField

class Seniunaitija(models.Model):
    name = InstitutionNameField()
    civilParish = InstitutionNameField()
    municipality = InstitutionNameField()

class SeniunaitijaStreet(models.Model):
    city = AddressNameField(null = True)
    street = AddressNameField(null = True)
    municipality = AddressNameField()
    seniunaitija = models.ForeignKey(Seniunaitija, null=True)
    numberFrom = models.IntegerField(null = True, db_index = True)
    numberTo = models.IntegerField(null = True, db_index = True)
    numberOdd = models.BooleanField()



class SeniunaitijaMember(models.Model):
    """ Seniunaitis. Is accountable to CivilParishMember. Basically he performs any sub-management
    compared to CivilParishMember. One hierarchy level deeper """
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    seniunaitija = models.ForeignKey(Seniunaitija, null=True)
    role = models.CharField(max_length = 20)
    phone = PhoneField()
    homePhone = PhoneField()
    uniqueKey = models.IntegerField()