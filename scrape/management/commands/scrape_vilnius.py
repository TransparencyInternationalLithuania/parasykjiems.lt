# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from scrape import utils


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from vilnius.lt.'''

    def handle(self, *args, **options):
        mayor = utils.get_rep(
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
                rep = utils.get_rep(url,
                              u'seniūnas',
                              [u'Seniūnas',
                               u'Seniūnė',
                               u'L. e. seniūno pareigas'],
                              mayor.institution + u' ' + inst)
                print rep
