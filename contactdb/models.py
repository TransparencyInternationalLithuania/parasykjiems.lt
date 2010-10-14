#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.fields import CharField
from enum import Enum


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

class PersonNameField(CharField):
    description = _("A person name field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        CharField.__init__(self, *args, **kwargs)





