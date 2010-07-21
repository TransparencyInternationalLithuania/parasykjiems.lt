#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

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
