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

    middle_title = soup.find('td', attrs={'class': 'middle-title'})

    for k in scrape_kinds:
        m = re.match(ur'{} (.*)'.format(re.escape(k)), middle_title.text)
        if m:
            rep_name = m.group(1)
            break
    assert(m)
    print rep_name

    kontaktai = soup.find('p', attrs={'class': 'kontaktiniai_duomenys'})
    rep_email = kontaktai.find('a',
                               attrs={'href': re.compile(ur'^mailto:')}).text
    print rep_email




class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from kaunas.lt.'''

    def handle(self, *args, **options):
        mayor = get_rep(
            'http://kaunas.lt/index.php?338403401',
            u'meras',
            [u'Meras'],
            u'Kauno miesto savivaldybė')
