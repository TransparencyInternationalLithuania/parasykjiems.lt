#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.db import models


class ParliamentMember(models.Model):
    electoralDistrict = models.CharField(max_length = 200)
    name = models.CharField(max_length = 50)
    surname = models.CharField(max_length = 50)
    email = models.CharField(max_length = 100)

    @property
    def fullName(self):
        """returns Name + surname"""
        return self.name + self.surname

    def __unicode__(self):
        return self.fullName


class County(models.Model):
    """ Contains counties, for example:
     County: Danės rinkimų apygarda Nr. 19
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
        
        return "CountyName: %s , nr: %d" % (self.name, number)
