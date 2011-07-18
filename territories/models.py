#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from contactdb.models import AddressNameField, Institution, HouseNumberField, HouseNumberOddField

class CountryAddress(models.Model):
    """ Contains a list of all streets in the country. Used to validate user input, when
    searching representatives with address"""

    municipality = AddressNameField(db_index = True)
    # http://en.wikipedia.org/wiki/Elderships_of_Lithuania
    # elderships are sometimes called CivilParish in the code. actually everywhere :)
    civilParish = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    city_genitive = AddressNameField(db_index = True)
    
    street = AddressNameField(db_index = True)


class LithuanianCase(models.Model):
    """ each Lithuanian object can be written in several cases. This mapping helps map from various form
    http://en.wikipedia.org/wiki/List_of_grammatical_cases """

    class Type:
        """ possible types of institution types"""
        Municipality = 1

    nominative = AddressNameField(db_index = True)
    genitive = AddressNameField(db_index = True)
    institutionType = models.IntegerField(db_index = True)


class InstitutionTerritory(models.Model):
    """ An institution territory defined by a list of addresses"""
    institution = models.ForeignKey(Institution)

    municipality = AddressNameField(db_index= True)
    civilParish = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    
    street = models.CharField(max_length=100,db_index = True)

    # house numbers are held in ranges from:to
    # numberOdd tells whether range is odd (1) or even (0)
    numberFrom = HouseNumberField()
    numberTo = HouseNumberField()
    numberOdd = HouseNumberOddField()

    comment = models.CharField(max_length=255,db_index = False)