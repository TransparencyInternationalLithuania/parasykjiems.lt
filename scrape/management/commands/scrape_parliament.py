# -*- coding: utf-8 -*-

import re
from django.core.management.base import BaseCommand
from scrape import utils


def normalise_name(name):
    return ' '.join(w.capitalize() for w in name.split())


def get_rep(url, delete=False):
    soup = utils.get_soup(url)
    table = soup.find('table', summary='Kadencijos')

    name_font = table.find('font', size='4')
    rep_name = normalise_name(name_font.text)

    info_td = table.find('td', valign='top')

    email_a = info_td.find('a', href=lambda s: s.startswith('mailto:'))
    rep_email = utils.email(email_a.get('href'))

    m = re.search(ur'Išrinktas *<b>([^<]+)</b> \((Nr. 39)\) apygardoje',
                  unicode(info_td))
    if m:
        ra_name = utils.normalise(m.group(1))
        ra_num = utils.normalise(m.group(2))
        inst_name = u'{} rinkimų apygarda {}'.format(ra_name, ra_num)
        multiple_reps = False
    else:
        inst_name = u'Išrinktas pagal sąrašą'
        multiple_reps = True

    m = re.search(ur'Darbo telefonas: </b><b>([^<]+)</b>', unicode(info_td))
    if m:
        rep_phone = utils.normalise(m.group(1))
    else:
        rep_phone = None

    utils.submit_rep_change(
        institution=inst_name,
        kind=u'Seimo narys',
        name=rep_name,
        email=rep_email,
        phone=rep_phone,
        multiple=multiple_reps,
        delete=delete)


class Command(BaseCommand):
    args = '<>'
    help = '''Data for members of parliament from lrs.lt.'''

    def handle(self, *args, **options):
        get_rep('http://www3.lrs.lt/pls/inter/w5_show?p_r=6113&p_k=1&p_a=5&'
                'p_asm_id=47856&p_kade_id=6')
