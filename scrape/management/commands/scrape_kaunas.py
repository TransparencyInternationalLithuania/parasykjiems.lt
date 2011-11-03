# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from scrape import utils
import re
from scrape import models


def get_phones(s):
    return ', '.join(p.strip()
                     for p in re.findall(r'[\s+\d+]+', s)
                     if re.search(r'\d', p))


def get_reps(url, canonic_kind, scrape_kinds, institution):
    soup = utils.get_soup(url)

    rep_kinds = soup.findAll('td', text=lambda x: x in scrape_kinds)
    rows = [rep_kind.findParent('tr') for rep_kind in rep_kinds]

    reps = []
    for row in rows:
        rep, created = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)

        kind, email_name, empty, room, phone = row.findAll('td')[:5]

        a = email_name.find('a')
        rep.name = utils.normalise(a.text)
        rep.email = utils.email(a.get('href'))
        print phone
        rep.phone = get_phones(utils.normalise(unicode(phone)))
        rep.save()
        reps.append(rep)
    return rep


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from kaunas.lt.'''

    def handle(self, *args, **options):
        mayor = get_reps(
            'http://kaunas.lt/index.php?1807955888',
            u'meras',
            [u'Meras'],
            u'Kauno miesto savivaldybė')
        print mayor
