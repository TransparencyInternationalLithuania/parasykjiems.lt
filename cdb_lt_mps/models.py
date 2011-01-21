#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
from contactdb.models import PersonNameField, AddressNameField

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


class PollingDistrictStreet(models.Model):
    """ Represents a mapping between a constituency, a district and a street in Lithuania
    """
    municipality = AddressNameField()
    constituency = models.ForeignKey(Constituency)
    street = AddressNameField(db_index = True)
    numberFrom = models.IntegerField(null = True, db_index = True)
    numberTo = models.IntegerField(null = True, db_index = True)
    numberOdd = models.IntegerField(null = True, db_index = True)
    city = AddressNameField(max_length = 50)
    pollingDistrict = models.CharField(max_length = 100)