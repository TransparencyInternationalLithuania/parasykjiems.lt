#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, InstitutionNameField, PhoneField

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
    officeEmail = models.EmailField()
    officePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    uniqueKey = models.IntegerField()

