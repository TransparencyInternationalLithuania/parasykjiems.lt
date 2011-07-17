#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging

from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.forms.extras.widgets import SelectDateWidget

from pjweb.widgets import hasNoProfanities, notEmptyMsg

logger = logging.getLogger(__name__)


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    """Renders horizontal radio buttons. Found here:
    https://wikis.utexas.edu/display/~bm6432/Django-Modifying+RadioSelect+Widget+to+have+horizontal+buttons
    """

    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class ContactForm(forms.Form):
    pub_choices = (
        ('private', _('Private')),
        ('public', _('Public')),
        )

    public = forms.ChoiceField(
        choices=pub_choices,
        initial=0,
        widget=forms.RadioSelect(renderer=HorizontalRadioRenderer),
        required=True)

    sender_name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'formTextInput'}),
        validators=[hasNoProfanities])

    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'formTextInput'}))

    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'email-body'}),
        validators=[hasNoProfanities, notEmptyMsg])

    sender = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'formTextInput'}))


class FeedbackForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'email-body'}))

    subject = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'formTextInput'}))

    emailFrom = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'formTextInput'}))


class IndexForm(forms.Form):
    address_input = forms.CharField(max_length=255)


class PeriodSelectForm(forms.Form):
    this_year = datetime.date.today().year

    date_from = forms.DateField(
        widget=SelectDateWidget(years=range(this_year, this_year - 5, -1)))

    date_to = forms.DateField(
        widget=SelectDateWidget(years=range(this_year, this_year - 5, -1)))
