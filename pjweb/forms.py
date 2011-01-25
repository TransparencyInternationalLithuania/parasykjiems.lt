#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import settings
from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy, ungettext
from django.core.exceptions import ValidationError
from pjweb.models import Email
from pjweb.widgets import *
from django.utils.safestring import mark_safe
from django.forms.extras.widgets import SelectDateWidget
import datetime

#from cdb_lt_streets.models import LithuanianStreetIndexes

#from autocomplete.widgets import AutoCompleteWidget
#from autocomplete.fields import ModelChoiceField

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
        widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=True)
    sender_name = forms.CharField(max_length=128, validators=[hasNoProfanities])
    phone = forms.CharField(max_length=100, validators=[hasDigits], required=False)
    message = forms.CharField(widget=forms.Textarea, validators=[hasNoProfanities,notEmptyMsg])
    sender = forms.EmailField()


class FeedbackForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)


#class StreetForm(forms.ModelForm):
#    class Meta:
#        model = LithuanianStreetIndexes
#    street = ModelChoiceField('street')


class IndexForm(forms.Form):
#    address_input = forms.CharField(widget=AutoCompleteWidget('street', force_selection=False))
    address_input = forms.CharField(max_length=255)


class PeriodSelectForm(forms.Form):

    this_year = datetime.date.today().year

    date_from = forms.DateField(widget=SelectDateWidget(years=range(this_year, this_year-5,-1)))
    date_to = forms.DateField(widget=SelectDateWidget(years=range(this_year, this_year-5,-1)))

