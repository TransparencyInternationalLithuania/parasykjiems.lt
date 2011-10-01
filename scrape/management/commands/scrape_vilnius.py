# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from scrape import models

from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
import re


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


def get_rep(url, canonic_kind, scrape_kinds, institution):
    soup = get_soup(url)

    tds = soup.find('table', attrs={'class': 'staff'}).findAll('td')
    kind_tds = [td for td in tds if contains_any(td, scrape_kinds)]
    if len(kind_tds):
        tr = kind_tds[0].findParent('tr')
        a = tr.find('a')

        rep = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)
        rep.name = normalise(a.text)
        rep.email = email(a.get('href'))
        rep.phone = normalise(tr.find('td', attrs={'class': 'r'}).text)
    else:
        print u"Failed to find {} in {}".format(canonic_kind, institution)
        rep = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)
        rep.delete = True

    rep.save()
    return rep


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from vilnius.lt.'''

    def handle(self, *args, **options):
        mayor = get_rep('http://www.vilnius.lt/newvilniusweb/index.php/15/',
                        u'meras',
                        [u'Meras'],
                        u'Vilniaus miesto savivaldybė')
        print mayor

        elderate_soup = get_soup(
            'http://www.vilnius.lt/newvilniusweb/index.php/49/')
        staff_table = elderate_soup.find('table', attrs={'class': 'staff'})
        for tr in staff_table.findAll('tr'):
            a = tr.find('a')
            if a:
                inst = normalise(a.text)
                url = a.get('href')
                rep = get_rep(url,
                              u'seniūnas',
                              [u'Seniūnas',
                               u'Seniūnė',
                               u'L. e. seniūno pareigas'],
                              mayor['institution'] + u' ' + inst)
                print rep
