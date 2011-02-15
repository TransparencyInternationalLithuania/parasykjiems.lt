#!/usr/bin/env python
# -*- coding: utf-8 -*-

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





