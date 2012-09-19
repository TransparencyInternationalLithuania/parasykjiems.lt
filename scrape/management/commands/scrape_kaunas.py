# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from scrape import utils
import re
import search.models


def get_phones(s):
    return ', '.join(p.strip()
                     for p in re.findall(r'[\s+\d+]+', s)
                     if re.search(r'\d', p))


def get_reps(url, canonic_kind, scrape_kinds, institution):
    soup = utils.get_soup(url)

    rep_kinds = soup.findAll('td', text=lambda x: x in scrape_kinds)
    rows = [rep_kind.findParent('tr') for rep_kind in rep_kinds]

    for row in rows:
        kind, email_name, empty, room, phone = row.findAll('td')[:5]
        a = email_name.find('a')
        utils.submit_rep_change(
            institution=institution,
            kind=canonic_kind,
            name=utils.normalise(a.text),
            email=utils.email(a.get('href')),
            phone=get_phones(utils.normalise(unicode(phone))))


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from kaunas.lt.'''

    def handle(self, *args, **options):
        inst = u'Kauno miesto savivaldybė'

        get_reps(
            'http://kaunas.lt/index.php?1807955888',
            u'meras',
            [u'Meras'],
            inst)

        utils.delay()

        elderates = (search.models.Institution.objects
                      .filter(name__startswith=inst,
                              name__endswith=u'seniūnija'))
        structure_page = utils.get_soup('http://kaunas.lt/index.php?58194844')

        for elderate in elderates:
            short_name = elderate.name[len(inst) + 1:]
            elderate_link = (structure_page
                             .find(name='a', text=lambda t: short_name in t)
                             .findParent())
            elderate_url = elderate_link.get('href')
            utils.delay()
            get_reps('http://kaunas.lt' + elderate_url,
                     u'seniūnas',
                     [u'Seniūnas',
                      u'Seniūnė'],
                      elderate.name)
