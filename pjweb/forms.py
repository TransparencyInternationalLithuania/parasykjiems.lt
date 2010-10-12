#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import settings
from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy, ungettext
from django.core.exceptions import ValidationError
from parasykjiems.contactdb.models import PollingDistrictStreet, Constituency, ParliamentMember, HierarchicalGeoData, MunicipalityMember, CivilParishMember, SeniunaitijaMember
from parasykjiems.pjweb.models import Email
from parasykjiems.pjweb.widgets import *
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    """renders horizontal radio buttons.
    found here:
    https://wikis.utexas.edu/display/~bm6432/Django-Modifying+RadioSelect+Widget+to+have+horizontal+buttons
    """

    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class ContactForm(forms.Form):
    pub_choices = (
        ('private',_('Private')),
        ('public',_('Public')),
    )
    public = forms.ChoiceField(choices = pub_choices,
        initial=0,
        widget=forms.RadioSelect(renderer=HorizontalRadioRenderer))
    sender_name = forms.CharField(max_length=128, validators=[hasNoProfanities])
    phone = forms.CharField(max_length=100, validators=[hasDigits], required=False)
    message = forms.CharField(widget=forms.Textarea, validators=[hasNoProfanities])
    sender = forms.EmailField()

class FeedbackForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)

class IndexForm(forms.Form):
    address_input = forms.CharField(max_length=255)
