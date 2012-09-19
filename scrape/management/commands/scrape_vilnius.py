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
    if kind_tds:
        tr = kind_tds[0].findParent('tr')
        a = tr.find('a')

        utils.submit_rep_change(
            institution=institution,
            kind=canonic_kind,
            name=utils.normalise(a.text),
            email=utils.email(a.get('href')),
            phone=get_phone(utils.normalise(
                unicode(tr.find('td', attrs={'class': 'r'})))))
    else:
        utils.submit_rep_change(
            institution=institution,
            kind=canonic_kind,
            delete=True)


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from vilnius.lt.'''

    def handle(self, *args, **options):
        municipality = u'Vilniaus miesto savivaldybė'

        get_rep(
            'http://www.vilnius.lt/newvilniusweb/index.php/15/',
            u'meras',
            [u'Meras'],
            municipality)

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
                get_rep(url,
                        u'seniūnas',
                        [u'Seniūnas',
                         u'Seniūnė',
                         u'L. e. seniūno pareigas'],
                         municipality + u' ' + inst)
