import csv
import os
import sys
import re

from django.core.management.base import BaseCommand, CommandError
from progressbar import ProgressBar
import itertools

from web.models import Representative, Territory, InstitutionType


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
            count = countlines(filename)
            f = open(filename, 'rb')
            reader = csv.DictReader(f)
            return ProgressBar(maxval=count)(reader)

        print 'Importing institution types.'
        
        old_name_to_new_type = {}
        
        for row in progressreader('data/new_institutiontypes.csv'):
            institution_type = InstitutionType(
                name=d(row['new_name']),
                representative_title=d(row['title']))
            institution_type.save()
            old_name_to_new_type[d(row['old_name'])] = institution_type
        
        old_id_to_new_type = {}
        
        for row in progressreader('data/institutiontypes.csv'):
            old_id = int(row['id'])
            old_name = d(row['name'])
            old_id_to_new_type[old_id] = old_name_to_new_type[old_name]

        print 'Importing representatives.'
        
        institution_to_representative_id = {}
        
        for row in itertools.chain(progressreader('data/personpositions.csv'),
                                   progressreader('data/institutions.csv')):
            institution_type = old_id_to_new_type[
                int(row['institution_type'])]
            representative = Representative(
                full_name=d(row['full_name']),
                institution_name=d(row['institution_name']),
                institution_type=institution_type,
                email=d(row['email']),
                contact_info=d(row['contact_info']))
            representative.save()
            institution_to_representative_id \
                [int(row['institution_id'])] = representative.id

        def separate_number(number_str):
            match = re.match(r'^(\d+)(.*)', number_str)
            if match:
                n, l = int(match.group(1)), match.group(2)
                return n, l
            else:
                return None, None

        print 'Importing territories.'
        
        for row in progressreader('data/institutionterritories.csv'):
            number_from, number_from_letters = \
                separate_number(d(row['number_from']))
            number_to, number_to_letters = \
                separate_number(d(row['number_to']))

            try:
                representative = Representative.objects.get(
                    id=institution_to_representative_id[int(row['institution_id'])])
                territory = Territory(
                    municipality=d(row['municipality']),
                    elderate=d(row['elderate']),
                    city=d(row['city']),
                    street=d(row['street']),
                    number_from=number_from,
                    number_from_letters=number_from_letters,
                    number_to=number_to,
                    number_to_letters=number_to_letters,
                    number_filter=d(row['number_filter']),
                    representative=representative)
                territory.save()
            except KeyError:
                print 'Institution {} not found.' \
                      .format(int(row['institution_id']))
