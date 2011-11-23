# -*- coding: utf-8 -*-

import re
from django.core.management.base import BaseCommand
from scrape import utils
from search.models import Representative
from lxml import html


def capital_name(name):
    return ' '.join(w.capitalize() for w in name.split())


def get_rep(url, delete=False):
    doc = html.parse(url)

    name_font = doc.xpath('//table[@summary="Kadencijos"]//font[@size="4"]')[0]
    rep_name = capital_name(name_font.text)

    info_td = doc.xpath('//table[@summary="Kadencijos"]//td[@valign="top"]')[0]

    m = re.search(ur'Išrinktas? +([^(]+) \((Nr. \d+)\) apygardoje',
                  utils.flat_text(info_td))
    if m:
        ra_name = utils.normalise(m.group(1))
        ra_num = utils.normalise(m.group(2))
        inst_name = u'{} rinkimų apygarda {}'.format(ra_name, ra_num)
        multiple_reps = False
    elif u'pagal sąrašą' in utils.flat_text(info_td):
        inst_name = u'Išrinktas pagal sąrašą'
        multiple_reps = True
    else:
        raise Exception("Can't find institution name.")

    if delete:
        rep_email = None
        rep_phone = None
    else:
        rep_email = utils.email(
            info_td.xpath('//a[starts-with(@href, "mailto:")]')[0].get('href'))

        m = re.search(ur'Darbo telefonas: *([^A]+)A',
                      utils.flat_text(info_td))
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


URL_ROOT = 'http://www3.lrs.lt/pls/inter/'
MEMBER_LIST_URL = URL_ROOT + 'w5_show?p_r=6113&p_k=1&p_a=12&p_kade_id=6'


class Command(BaseCommand):
    args = '<>'
    help = '''Data for members of parliament from lrs.lt.'''

    def handle(self, *args, **options):
        for rep in Representative.objects.filter(
                kind__name=u'Seimo narys',
                institution__name=u'Išrinktas pagal sąrašą'):
            utils.submit_rep_change(
                kind=u'Seimo narys',
                institution=u'Išrinktas pagal sąrašą',
                name=rep.name,
                multiple=True,
                delete=True)

        doc = html.parse(MEMBER_LIST_URL).getroot()
        doc.make_links_absolute()
        member_links = doc.xpath(
            u'//table[@summary="Seimo narių sarašas pagal apygardas"]'
            u'//a[contains(@href, "p_asm_id=")]')
        for a in member_links:
            utils.delay()
            url = a.get('href')
            delete = a.tail and u'(' in a.tail
            get_rep(url, bool(delete))
