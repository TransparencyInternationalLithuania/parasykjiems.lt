import csv
import os
import sys
import re

from django.core.management.base import BaseCommand, CommandError

from web.models import Representative, Territory, InstitutionType


class Command(BaseCommand):
    args = '<>'
    help = "Imports data from CSV's created by export.py into database."


    def handle(self, *args, **options):
        def d(s):
            return s.decode('utf-8')
        
        old_name_to_new_type = {}
        
        with open('data/new_institutiontypes.csv', 'rb') as f:
            r = csv.DictReader(f)
            for row in r:
                institution_type = InstitutionType(
                    name=d(row['new_name']),
                    representative_title=d(row['title']))
                institution_type.save()
                print institution_type
                old_name_to_new_type[d(row['old_name'])] = institution_type
        
        old_id_to_new_type = {}
        
        with open('data/institutiontypes.csv', 'rb') as f:
            r = csv.DictReader(f)
            for row in r:
                old_id = int(row['id'])
                old_name = d(row['name'])
                old_id_to_new_type[old_id] = old_name_to_new_type[old_name]
        
        institution_to_representative_id = {}
        
        with open('data/personpositions.csv', 'rb') as f:
            r = csv.DictReader(f)
            for row in r:
                institution_type = old_id_to_new_type[
                    int(row['institution_type'])]
                representative = Representative(
                    full_name=d(row['full_name']),
                    institution_name=d(row['institution_name']),
                    institution_type=institution_type,
                    email=d(row['email']),
                    contact_info=d(row['contact_info']))
                representative.save()

                representative.id
                print representative
        
        _num_regex = re.compile(r'^(\d+)(.*)')
        def separate_number(number_str):
            match = re.match(_num_regex, number_str)
            return int(match.group(1)), match.group(2)
        
        with open('data/institutionterritories.csv', 'rb') as f:
            r = csv.DictReader(f)
            for row in r:
                number_from, number_from_letters = \
                             separate_number(d(row['number_from']))
                number_to, number_to = separate_number(d(row['number_to']))
                
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
                    representative=Representative.objects.get(
                        id=institution_to_representative_id[
                            int(row['institution_id'])]))
                territory.save()
                print territory
