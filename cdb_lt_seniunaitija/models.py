#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, PhoneField, InstitutionNameField

class Seniunaitija(models.Model):
    name = InstitutionNameField();

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