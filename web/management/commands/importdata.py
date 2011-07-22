import csv
import re

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from progressbar import ProgressBar, Bar, ETA

from web.models import \
     InstitutionKind, Institution, \
     RepresentativeKind, Representative, \
     Territory


class Command(BaseCommand):
    args = '<>'
    help = "Imports data from CSV's created by export.py into database."


    def handle(self, *args, **options):
        def d(s):
            return s.decode('utf-8')

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
        
        for row in progressreader('data/new_institutiontypes.csv'):
            inst = InstitutionKind(
                name=d(row['new_name']),
                description=u'')
            inst.save()
            old_name_to_new_inst[d(row['old_name'])] = inst
            rep = RepresentativeKind(
                name=d(row['title']),
                description=u'')
            rep.save()
            inst_to_rep[inst] = rep
        
        old_id_to_new_inst = {}
        
        for row in progressreader('data/institutiontypes.csv'):
            old_id = int(row['id'])
            old_name = d(row['name'])
            if old_name in old_name_to_new_inst:
                old_id_to_new_inst[old_id] = old_name_to_new_inst[old_name]

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
                    phone=d(row['phone']),
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
                    phone=d(row['phone']),
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
                return int(n), l.upper()
            else:
                return None, None

        skips = 0
        imports = 0
        merges = 0
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
                else:
                    numbers.append(u'{}-{}{}'.format(num_from, num_to, suffix))

                if num_from_letter:
                    numbers.append(u'{}{}'.format(num_from, num_from_letter))
                if num_to_letter:
                    numbers.append(u'{}{}'.format(num_to, num_to_letter))
            elif num_from:
                numbers.append(u'{}{}'.format(num_from, num_from_letter))
            elif num_to:
                print 'Strange number range: {}'.format(row)

            try:
                institution = \
                    Institution.objects.get(id=int(row['institution_id']))
                municipality=d(row['municipality'])
                city=d(row['city'])
                street=d(row['street'])
            
                maybe_territory = list(Territory.objects.filter(
                    institution=institution,
                    municipality=municipality,
                    city=city,
                    street=street))

                if maybe_territory == []:
                    territory = Territory(
                        institution=institution,
                        municipality=municipality,
                        city=city,
                        street=street,
                        numbers=', '.join(numbers))
                    territory.save()
                    imports += 1
                else:
                    territory = maybe_territory[0]
                    territory.numbers = ', '.join([territory.numbers] + numbers)
                    merges += 1
            except ObjectDoesNotExist:
                skips += 1
        print 'Imported {} territories, with {} merges. Skipped {}.'.format(imports, merges, skips)
