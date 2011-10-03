# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from scrape import utils
import re
from scrape import models


def get_phone(s):
    m = re.search(r'(\(.+\))?(\s+\d+)?\s+\d+', s)
    if m:
        return m.group(0)
    else:
        return u''


def get_rep(url, canonic_kind, scrape_kinds, institution):
    soup = utils.get_soup(url)

    tds = soup.find('table', attrs={'class': 'staff'}).findAll('td')
    kind_tds = [td for td in tds if utils.contains_any(td, scrape_kinds)]
    if len(kind_tds):
        tr = kind_tds[0].findParent('tr')
        a = tr.find('a')

        rep, created = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)
        rep.name = utils.normalise(a.text)
        rep.email = utils.email(a.get('href'))
        rep.phone = get_phone(utils.normalise(
            unicode(tr.find('td', attrs={'class': 'r'}))))
    else:
        rep, created = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)
        rep.delete = True

    rep.save()
    return rep


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from vilnius.lt.'''

    def handle(self, *args, **options):
        mayor = get_rep(
            'http://www.vilnius.lt/newvilniusweb/index.php/15/',
            u'meras',
            [u'Meras'],
            u'Vilniaus miesto savivaldybė')
        print mayor

        utils.delay()
        elderate_soup = utils.get_soup(
            'http://www.vilnius.lt/newvilniusweb/index.php/49/')
        staff_table = elderate_soup.find('table', attrs={'class': 'staff'})
        for tr in staff_table.findAll('tr'):
            a = tr.find('a')
            if a:
                inst = utils.normalise(a.text)
                url = a.get('href')
                utils.delay()
                rep = get_rep(url,
                              u'seniūnas',
                              [u'Seniūnas',
                               u'Seniūnė',
                               u'L. e. seniūno pareigas'],
                              mayor.institution + u' ' + inst)
                print rep
