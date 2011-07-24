# -*- coding: utf-8 -*-

import csv
import re

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from progressbar import ProgressBar, Bar, ETA

from web.models import \
     InstitutionKind, Institution, \
     RepresentativeKind, Representative, \
     Street, Territory


_INSTITUTION_TYPE_CONVERSIONS = (
    {'old_name': u"Civil parish member",
      'institution': u"seniūnija",
      'representative': u"seniūnas",
      'active': True},
    {'old_name': u"Mayor",
      'institution': u"savivaldybė",
      'representative': u"meras",
      'active': True},
    {'old_name': u"Member of parliament",
      'institution': u"Seimas",
      'representative': u"Seimo narys",
      'active': True},
    {'old_name': u"Seniūnaitis",
      'institution': u"seniūnaitija",
      'representative': u"seniūnaitis",
      'active': False},
)


class Command(BaseCommand):
    args = '<>'
    help = "Imports data from CSV's created by export.py into database."

    def handle(self, *args, **options):
        def d(s):
            return s.decode('utf-8').strip()

        def dphone(p):
            dp = d(p)
            if dp == u'-':
                return u''
            else:
                # Normalise phone number
                return dp\
                       .replace(u';', u',')\
                       .replace(u'~', u'-')\
                       .replace(u'( ', u'(')\
                       .replace(u' )', u')')\
                       .replace(u' ,', u', ')\
                       .replace(u' /', u',')

        def countlines(filename):
            with open(filename) as f:
                for i, l in enumerate(f):
                    pass
            return i + 1

        def progressreader(filename):
            print 'Importing from "{}":'.format(filename)
            count = countlines(filename)
            f = open(filename, 'rb')
            reader = csv.DictReader(f)
            widgets = [ETA(), ' ', Bar()]
            return ProgressBar(widgets=widgets, maxval=count)(reader)

        old_name_to_new_inst = {}
        inst_to_rep = {}

        for c in _INSTITUTION_TYPE_CONVERSIONS:
            inst = InstitutionKind(
                name=c['institution'],
                active=c['active'],
                description=u'')
            inst.save()
            old_name_to_new_inst[c['old_name']] = inst
            rep = RepresentativeKind(
                name=c['representative'],
                active=c['active'],
                description=u'')
            rep.save()
            inst_to_rep[inst] = rep

        old_id_to_new_inst = {}

        for row in progressreader('data/institutiontypes.csv'):
            old_id = int(row['id'])
            old_name = d(row['name'])
            if old_name in old_name_to_new_inst:
                old_id_to_new_inst[old_id] = old_name_to_new_inst[old_name]
            else:
                print u'Not importing {} institutions.'.format(old_name)

        skips = 0
        imports = 0
        for row in progressreader('data/institutions.csv'):
            type_id = int(row['type_id'])
            if type_id in old_id_to_new_inst:
                inst = Institution(
                    id=int(row['id']),
                    name=d(row['name']),
                    kind=old_id_to_new_inst[type_id],
                    email=d(row['email']),
                    phone=dphone(row['phone']),
                    address=d(row['address']))
                inst.save()
                imports += 1
            else:
                skips += 1
        print 'Imported {} institutions.'.format(imports)
        print 'Skipped {} institutions.'.format(skips)

        skips = 0
        imports = 0
        for row in progressreader('data/personpositions.csv'):
            try:
                inst = Institution.objects.get(id=int(row['institution_id']))
                representative = Representative(
                    name=d(row['name']),
                    institution=inst,
                    kind=inst_to_rep[inst.kind],
                    email=d(row['email']),
                    phone=dphone(row['phone']),
                    other_contacts=d(row['other_contacts']))
                representative.save()
                imports += 1
            except ObjectDoesNotExist:
                skips += 1
        print 'Imported {} representatives.'.format(imports)
        print 'Skipped {} representatives.'.format(skips)

        def separate_number(number_str):
            match = re.match(r'^(\d+)(.)$', number_str)
            if match:
                n, l = match.group(1), match.group(2)
                if l == '0':
                    l = ''
                return int(n), l.upper()
            else:
                return None, None

        skips = 0
        imports = 0
        merges = 0
        streets = 0
        large_numbers = set()
        for row in progressreader('data/institutionterritories.csv'):
            num_from, num_from_letter = \
                separate_number(d(row['number_from']))
            num_to, num_to_letter = \
                separate_number(d(row['number_to']))

            num_filter = d(row['number_filter'])

            numbers = []
            if num_from and num_to:
                if num_filter != 'all':
                    suffix = u' {}'.format(num_filter)
                else:
                    suffix = u''

                if num_to > 900:
                    numbers.append(u'{}-{}'.format(num_from, suffix))
                    large_numbers.add(num_to)
                else:
                    numbers.append(u'{}-{}{}'.format(num_from, num_to, suffix))

                if num_from_letter:
                    numbers.append(u'{}{}'.format(num_from, num_from_letter))
                if num_to_letter:
                    numbers.append(u'{}{}'.format(num_to, num_to_letter))
            elif num_from:
                numbers.append(u'{}{}'.format(num_from, num_from_letter))
            elif num_to:
                print 'Strange number range in {}'.format(row)
                continue

            try:
                institution = \
                    Institution.objects.get(id=int(row['institution_id']))
                municipality = d(row['municipality'])
                city = d(row['city'])
                street = d(row['street'])

                maybe_street_obj = Street.objects.filter(
                    municipality=municipality,
                    city=city,
                    street=street)

                if maybe_street_obj.exists():
                    street_obj = maybe_street_obj[0]
                else:
                    street_obj = Street(
                        municipality=municipality,
                        city=city,
                        street=street)
                    street_obj.save()
                    streets += 1

                maybe_territory = Territory.objects.filter(
                    institution=institution,
                    street=street_obj)

                if maybe_territory.exists():
                    territory = maybe_territory[0]
                    if territory.numbers == '':
                        print u'Warning: not replacing empty numbers with more specific numbers [{}] in {}' \
                              .format(numbers, territory)
                    else:
                        territory.numbers = ', '.join(
                            [territory.numbers] + numbers)
                    territory.save()
                    merges += 1
                else:
                    territory = Territory(
                        institution=institution,
                        street=street_obj,
                        numbers=', '.join(numbers))
                    territory.save()
                    imports += 1
            except ObjectDoesNotExist:
                skips += 1
        print 'Imported {} territories, {} streets, with {} merges. Skipped {}.'.\
              format(imports, streets, merges, skips)
        print 'Numbers turned into infinities: {}'.format(large_numbers)
