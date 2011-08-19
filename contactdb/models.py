#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext as _
from django.db.models.fields import CharField, IntegerField, NullBooleanField

class PhoneField(CharField):
    description = _("Phone field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 127)
        CharField.__init__(self, *args, **kwargs)

class InstitutionNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        CharField.__init__(self, *args, **kwargs)

class AddressNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)

class HouseNumberField(CharField):
    description = _("A house number field, capable of storing house letter")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 10)
        kwargs['db_index'] = kwargs.get('db_index', True)
        kwargs['null'] = kwargs.get('null', False)
        CharField.__init__(self, *args, **kwargs)


class HouseNumberOddField(NullBooleanField):
    description = _("Tells whether a house number is odd or even")

    def __init__(self, *args, **kwargs):
        kwargs['db_index'] = kwargs.get('db_index', True)
        kwargs['null'] = kwargs.get('null', True)
        NullBooleanField.__init__(self, *args, **kwargs)


class PersonNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)





class Person(models.Model):
    name = PersonNameField()
    surname = PersonNameField()
    # this is an additional field, which, together with name and surname form a unique key
    # We do not enfore this at the database level, as we do not want our scripts to fail prematurely (yet)
    # unique_together = (("name", "surname", "disambiguation"),)
    disambiguation = PersonNameField(blank=True,null=True)

    # used to uniquely identify persons
    # For example, if a person name or surname has changed, this will be used to locate the Person in question
    uniqueKey = models.IntegerField(null=True,blank=True)

    @property
    def fullName(self):
        return u"%s %s" % (self.name, self.surname)

    def __unicode__(self):
        return u" ".join(x for x in [self.name, self.surname, self.disambiguation] if x)

class InstitutionType(models.Model):
    # a code which identifies what kind of institution is this (parliament, mayor, etc)
    # This is user generated value, when inital value is inserted
    code = models.CharField(max_length = 255)

    def __unicode__(self):
        return self.code

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
    primaryPhone = PhoneField(blank=True)
    secondaryPhone = PhoneField(blank=True)

    # a date range when this position was occupied
    electedFrom = models.DateField(null=True, blank=True)
    electedTo = models.DateField(null=True, blank=True)

    @classmethod
    def getFilterActivePositions(cls):
        electedToNone = Q(**{"electedTo" : None})
        electedFromNone = Q(**{"electedFrom" : None})
        now = datetime.now()
        electedToGreaterToday = Q(**{"electedTo__gte": now})
        electedFromLessThanToday = Q(**{"electedFrom__lte": now})
        return (electedToNone & electedFromNone) | ((electedFromNone | electedFromLessThanToday) & (electedToNone | electedToGreaterToday))

    def __unicode__(self):
        return u'(%d) %s in %s' % (self.id, self.person, self.institution)
