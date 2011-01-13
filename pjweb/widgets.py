#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _, ugettext_lazy, ungettext
from django.core.exceptions import ValidationError
from django import forms
from settings import *
import re
from django.utils.translation import ugettext as _

def convertLithuanianLettersToLatin(str):
    """ converts Lithuanian """
    str = str.replace(u"ą", u"a")
    str = str.replace(u"č", u"c")
    str = str.replace(u"ę", u"e")
    str = str.replace(u"ė", u"e")
    str = str.replace(u"į", u"i")
    str = str.replace(u"š", u"s")
    str = str.replace(u"ų", u"u")
    str = str.replace(u"ū", u"u")
    str = str.replace(u"ž", u"z")
    return str
    

def hasNoProfanities(field_data):
    """ 
    Checks that the given string has no profanities in it. This does a simple 
    check for whether each profanity exists within the string, so 'fuck' will 
    catch 'motherfucker' as well. Raises a ValidationError such as: 
       Watch your mouth! The words "f--k" and "s--t" are not allowed here. 
    """ 
    field_data = field_data.lower() # normalize
    field_data = convertLithuanianLettersToLatin(field_data)
    words_seen = [w for w in GlobalSettings.PROFANITIES_LIST if w in field_data] 
    if words_seen: 
        from django.utils.text import get_text_list 
        plural = len(words_seen) 
        raise ValidationError, _('Please be polite! Letter with %s in it will not be sent.') % get_text_list(
                ['"%s%s%s"' % (i[0], '-'*(len(i)-2), i[-1]) for i in words_seen], _('and')
            )

def hasDigits(field_data):

    field_data = field_data.lower()
    if not re.match("^[+() 0-9]*$", field_data):
        raise ValidationError, _('There should be numbers in phone number.')

def notEmptyMsg(field_data):
    words = field_data.split(' ')
    text = field_data.replace('\r','')
    name = words[2]
    to_check = _(u'Dear. Mr. %s \n\n\n\nHave a nice day.') % name
    if text==to_check:
        raise ValidationError, _('Message should not only be greeting.')

