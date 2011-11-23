# -*- coding: utf-8 -*-

import time
import re
import random
import urllib2
from BeautifulSoup import BeautifulSoup
import models
from search.models import Institution, RepresentativeKind


_MULTIPLE_SPACES = re.compile(r'\s\s+')
_NBSP = u'\xa0'


def normalise(s):
    return (_MULTIPLE_SPACES
            .sub(' ', s.replace(_NBSP, ' ').strip())
            .replace(' - ', '-'))


def email(s):
    if s.startswith('mailto:'):
        return s[len('mailto:'):]
    else:
        return s


USER_AGENT = 'ParasykJiems (http://parasykjiems.lt/contact/)'


def get_soup(url, encoding=None):
    headers = {'User-agent': USER_AGENT}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    return BeautifulSoup(response,
                         convertEntities=BeautifulSoup.HTML_ENTITIES,
                         fromEncoding=encoding)


def contains_any(s, substrings):
    return any(substring in s for substring in substrings)


def delay():
    time.sleep(min(30, max(1, random.normalvariate(5, 5))))


def submit_rep_change(institution, kind,
                      delete=False, multiple=False,
                      name=None, email=None, phone=None, other_info=None):
    change, created = models.RepresentativeChange.objects.get_or_create(
        institution=Institution.objects.get(name=institution),
        kind=RepresentativeKind.objects.get(name=kind),
        name=name, email=email, phone=phone, other_info=other_info,
        multiple=multiple, delete_rep=delete)
    if change.changed():
        change.save()
        return change
    else:
        change.delete()
        return None


def submit_inst_change(institution,
                       email=None, phone=None, other_info=None, address=None):
    inst, created = models.InstitutionChange.objects.get_or_create(
        institution=Institution.objects.get(name=institution))

    inst.email = email
    inst.phone = phone
    inst.other_info = other_info
    inst.address = address

    if inst.changed():
        inst.save()
        return inst
    else:
        inst.delete()
        return None


def flat_text(element):
    """Returns a flat string of all the text contained in the lxml
    document.
    """
    return ''.join(element.itertext())
