#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, PhoneField, InstitutionNameField

class Municipality(models.Model):
    name = InstitutionNameField()

class MunicipalityMember(models.Model):
    name = PersonNameField()
    surname = PersonNameField()
    email = models.EmailField()
    email2 = models.EmailField()
    municipality = models.ForeignKey(Municipality, null=True)
    phone = PhoneField()
    phone2 = PhoneField()
    mobilePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    uniqueKey = models.IntegerField()