#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.fields import CharField, IntegerField

class PhoneField(CharField):
    description = _("Phone field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 20)
        CharField.__init__(self, *args, **kwargs)

class InstitutionNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)

class AddressNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)

class HouseNumberField(CharField):
    description = _("A house number field, capable of storing house letter")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 5)
        kwargs['db_index'] = kwargs.get('db_index', True)
        kwargs['null'] = kwargs.get('null', False)
        CharField.__init__(self, *args, **kwargs)


class HouseNumberOddField(IntegerField):
    description = _("Tells whether a house number is odd or even")

    def __init__(self, *args, **kwargs):
        kwargs['db_index'] = kwargs.get('db_index', True)
        kwargs['null'] = kwargs.get('null', True)
        IntegerField.__init__(self, *args, **kwargs)


class PersonNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)





class Person(models.Model):
    name = PersonNameField()
    surname = PersonNameField()
    # used to uniquely identify persons
    # For example, if a person name or surname has changed, this will be used to locate the Person in question
    uniqueKey = models.IntegerField()

    @property
    def fullName(self):
        """returns Name + surname"""
        return self.name + self.surname

    def __unicode__(self):
        return self.fullName

class InstitutionType(models.Model):
    # a code which identifies what kind of institution is this (parliament, mayor, etc)
    # This is user generated value, when inital value is inserted
    code = models.CharField(max_length = 10)

class Institution(models.Model):
    """ A local institution. Contains institution name, and institution type"""
    name = InstitutionNameField()
    officeEmail = models.EmailField()
    officePhone = PhoneField()
    officeAddress = models.CharField(max_length = 100)
    
    # Every institution must be categorized. For example a civil parish, parliament, etc
    institutionType = models.ForeignKey(InstitutionType, null=False)
    def __unicode__(self):
        return self.name

class PersonPosition(models.Model):
    """ Relates a person to institution.
    Allows single person to be elected in several institutions at once"""
    person = models.ForeignKey(Person, null=False)
    institution = models.ForeignKey(Institution, null=False)

    # contact information
    email = models.EmailField()
    primaryPhone = PhoneField()
    secondaryPhone = PhoneField()

    # a date range when this position was occupied
    electedFrom = models.DateField(null=True)
    electedTo = models.DateField(null=True)
