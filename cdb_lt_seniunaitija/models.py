#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, PhoneField, InstitutionNameField, AddressNameField, HouseNumberField, HouseNumberOddField

class Seniunaitija(models.Model):
    name = InstitutionNameField()
    civilParish = InstitutionNameField()
    municipality = InstitutionNameField()

class SeniunaitijaStreet(models.Model):
    institution = models.ForeignKey(Seniunaitija)
    municipality = AddressNameField(db_index= True)
    civilParish = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    street = AddressNameField(db_index = True)
    numberFrom = HouseNumberField()
    numberTo = HouseNumberField()
    numberOdd = HouseNumberOddField()


class SeniunaitijaMember(models.Model):
    """ Seniunaitis. Is accountable to CivilParishMember. Basically he performs any sub-management
    compared to CivilParishMember. One hierarchy level deeper """
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    institution = models.ForeignKey(Seniunaitija, null=True)
    role = models.CharField(max_length = 20)
    phone = PhoneField()
    homePhone = PhoneField()
    uniqueKey = models.IntegerField()