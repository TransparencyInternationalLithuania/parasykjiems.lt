# -*- coding: utf-8 -*-

import re
from django.core.management.base import BaseCommand
from unidecode import unidecode
from scrape import utils


EXCLUDE_MAYORS = [
    u'Vilniaus miesto savivaldybė',
    u'Kauno miesto savivaldybė'
]


def get_municipality(url):
    soup = utils.get_soup(url)

    header = soup.find('font', face='arial', size='3')

    inst_name = utils.normalise(header.text)

    table2 = header.findParent('td').findParent('td').findAll('table')[1]
    info = table2.find('font')

    rep_name = utils.normalise(info.find('b').text)

    rep_ascii_first_name = unidecode(rep_name.split()[0].lower())

    a = info.find('a', href=lambda h: h.startswith('mailto:'))
    email = utils.email(a.get('href'))
    inst_email = None
    rep_email = None
    if email != '':
        if ('meras' in email or
            email.startswith(rep_ascii_first_name)):
            rep_email = email
        else:
            inst_email = email

    m = re.search('>([^<]+)<br', unicode(info))
    inst_address = utils.normalise(m.group(1)) if m else ''

    m = re.search(r'tel\. ([^,]+),', info.text)
    inst_phone = utils.normalise(m.group(1)) if m else ''
    if inst_phone == '':
        inst_phone = None

    m = re.search(r'Meras.*tel\. ([^,]+),', info.text)
    rep_phone = utils.normalise(m.group(1)) if m else ''
    if rep_phone == '':
        rep_phone = None

    utils.submit_inst_change(
        institution=inst_name,
        phone=inst_phone,
        email=inst_email,
        address=inst_address)

    if inst_name not in EXCLUDE_MAYORS:
        utils.submit_rep_change(
            institution=inst_name,
            kind='meras',
            name=rep_name,
            email=rep_email,
            phone=rep_phone)


class Command(BaseCommand):
    args = '<>'
    help = '''Scrape municipality and elderate data from kaunas.lt.'''

    def handle(self, *args, **options):
        root = 'http://www.savivaldybes.lt/savivaldybes/'
        soup = utils.get_soup(root)
        link_texts = soup.findAll(text=lambda t: t.endswith(u'savivaldybė'))
        for link_text in link_texts:
            utils.delay()
            link = link_text.findParent()
            url = root + link.get('href')
            get_municipality(url)
