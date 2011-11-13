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
    return _MULTIPLE_SPACES.sub(' ', s.replace(_NBSP, ' ').strip())


def email(s):
    if s.startswith('mailto:'):
        return s[len('mailto:'):]
    else:
        return s


USER_AGENT = 'ParasykJiems (http://parasykjiems.lt/contact/)'


def get_soup(url):
    headers = {'User-agent': USER_AGENT}
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    return BeautifulSoup(response, convertEntities=BeautifulSoup.HTML_ENTITIES)


def contains_any(s, substrings):
    return any(substring in s for substring in substrings)


def delay():
    time.sleep(min(30, max(1, random.normalvariate(5, 5))))


def submit_rep_change(institution, kind,
                      delete=False,
                      name=None, email=None, phone=None, other_info=None):
    rep, created = models.RepresentativeChange.objects.get_or_create(
        institution=Institution.objects.get(name=institution),
        kind=RepresentativeKind.objects.get(name=kind))
    if delete:
        rep.delete_rep = True
    else:
        rep.name = name
        rep.email = email
        rep.phone = phone
        rep.other_info = other_info
    if rep.changed():
        rep.save()
        print rep
        return rep
    else:
        rep.delete()
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
        print inst
        return inst
    else:
        inst.delete()
        return inst
