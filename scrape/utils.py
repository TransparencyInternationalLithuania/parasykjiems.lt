import time
import re
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
import models


_MULTIPLE_SPACES = re.compile(r'\s\s+')
_NBSP = u'\xa0'


def normalise(s):
    return _MULTIPLE_SPACES.sub(' ', s.replace(_NBSP, ' ').strip())


def email(s):
    if s.startswith('mailto:'):
        return s[len('mailto:'):]
    else:
        return s


def get_soup(url):
    response = urlopen(url)
    return BeautifulSoup(response, convertEntities=BeautifulSoup.HTML_ENTITIES)


def contains_any(s, substrings):
    return any(substring in s for substring in substrings)


def delay():
    time.sleep(1)


def submit_rep_change(institution, kind,
                      delete=False,
                      name=None, email=None, phone=None, other_info=None):
    rep, created = models.RepresentativeChange.objects.get_or_create(
        institution=institution,
        kind_name=kind)
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


def submit_inst_change(name, email=None, phone=None, other_info=None):
    inst, created = models.InstitutionChange.objects.get_or_create(
        name=name)

    inst.email = email
    inst.phone = phone
    inst.other_info = other_info

    if inst.changed():
        inst.save()
        print inst
        return inst
    else:
        inst.delete()
        return inst
