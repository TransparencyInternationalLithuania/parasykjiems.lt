# -*- coding: utf-8 -*-

import re
from django.core.management.base import BaseCommand
from scrape import utils


def get_municipality(url):
    soup = utils.get_soup(url)

    header = soup.find('font', face='arial', size='3')

    inst_name = utils.normalise(header.text)

    table2 = header.findParent('td').findParent('td').findAll('table')[1]
    info = table2.find('font')

    rep_name = utils.normalise(info.find('b').text)

    a = info.find('a', href=lambda h: h.startswith('mailto:'))
    inst_email = utils.email(a.get('href'))

    m = re.search('>([^<]+)<br', unicode(info))
    inst_other_info = utils.normalise(m.group(1)) if m else ''

    m = re.search(r'tel\. ([^,]+),', info.text)
    inst_phone = utils.normalise(m.group(1)) if m else ''

    m = re.search(r'Meras.*tel\. ([^,]+),', info.text)
    rep_phone = utils.normalise(m.group(1)) if m else ''

    print inst_name
    utils.submit_inst_change(
        name=inst_name,
        phone=inst_phone,
        email=inst_email,
        other_info=inst_other_info)

    utils.submit_rep_change(
        institution=inst_name,
        kind='meras',
        name=rep_name,
        email=None,
        phone=rep_phone)


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from kaunas.lt.'''

    def handle(self, *args, **options):
        root = 'http://www.savivaldybes.lt/savivaldybes/'
        soup = utils.get_soup(root)
        link_texts = soup.findAll(text=lambda t: t.endswith(u'savivaldybė'))
        for link_text in link_texts:
            link = link_text.findParent()
            url = root + link.get('href')
            get_municipality(url)
