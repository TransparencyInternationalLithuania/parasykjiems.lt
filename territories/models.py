#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from contactdb.models import AddressNameField, Institution, HouseNumberField, HouseNumberOddField

class CountryAddresses(models.Model):
    """ Contains a list of all streets in the country. Used to validate user input, when
    searching representatives with address"""

    municipality = AddressNameField(db_index = True)
    # http://en.wikipedia.org/wiki/Elderships_of_Lithuania
    # elderships are sometimes called CivilParish in the code. actually everywhere :)
    civilparish = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    city_genitive = AddressNameField(db_index = True)
    
    street = AddressNameField(db_index = True)




class InstititutionTerritory(models.Model):
    """ An institution territory defined by a list of addresses"""
    institution = models.ForeignKey(Institution)

    municipality = AddressNameField(db_index= True)
    civilParish = AddressNameField(db_index = True)
    city = AddressNameField(db_index = True)
    
    street = AddressNameField(db_index = True)

    # house numbers are held in ranges from:to
    # numberOdd tells whether range is odd (1) or even (0)
    numberFrom = HouseNumberField()
    numberTo = HouseNumberField()
    numberOdd = HouseNumberOddField()