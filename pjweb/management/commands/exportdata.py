import csv
import os
import sys
import re

from django.core.management.base import BaseCommand, CommandError
from progressbar import ProgressBar

from contactdb.models import InstitutionType, PersonPosition, Institution
from territories.models import InstitutionTerritory, LithuanianCases

class Command(BaseCommand):
    args = '<>'
    help = """Exports all data from the database into a more sensible format.

Puts results in CSV files into the export directory.
"""

    def handle(self, *args, **options):
        if not os.path.exists('export'):
            os.mkdir('export')
        
        def e(s):
            return s.encode('utf-8')
        
        print 'Exporting {} InstitutionTypes.'.format(
            len(InstitutionType.objects.all()))
        with open('export/institutiontypes.csv', 'wb') as f:
            w = csv.DictWriter(f,
                               ['id',
                                'name'])
            w.writeheader()
            for it in ProgressBar()(InstitutionType.objects.all()):
                w.writerow({'id': str(it.id),
                            'name': e(it.code)})

        institutions_with_persons = set()
        
        print 'Exporting {} PersonPositions.'.format(
            len(PersonPosition.objects.all()))
        with open('export/personpositions.csv', 'wb') as f:
            w = csv.DictWriter(f,
                               ['full_name',
                                'institution_name',
                                'institution_id',
                                'institution_type',
                                'email',
                                'phone',
                                'address'])
            w.writeheader()
            for p in ProgressBar()(PersonPosition.objects.all()):
                w.writerow({'full_name': e(p.person.fullName),
                            'institution_name': e(p.institution.name),
                            'institution_id': str(p.institution.id),
                            'institution_type': str(p.institution.institutionType.id),
                            'email': e(p.email),
                            'phone': e(p.primaryPhone or p.secondaryPhone),
                            'address': e(p.institution.officeAddress)})

                institutions_with_persons.add(p.institution.id)

        print 'Exporting {} Institutions without persons.'.format(
            len(Institution.objects.all()) - len(PersonPosition.objects.all()))
        with open('export/institutions.csv', 'wb') as f:
            w = csv.DictWriter(f,
                               ['full_name',
                                'institution_name',
                                'institution_id',
                                'institution_type',
                                'email',
                                'phone',
                                'address'])
            w.writeheader()
            for i in ProgressBar()(Institution.objects.all()):
                if i.id not in institutions_with_persons:
                    w.writerow({'full_name': '',
                                'institution_name': e(i.name),
                                'institution_id': str(i.id),
                                'institution_type': str(i.institutionType.id),
                                'email': e(i.officeEmail),
                                'phone': e(i.officePhone),
                                'address': e(i.officeAddress)})

        print 'Exporting {} InstitutionTerritories.'.format(
            len(InstitutionTerritory.objects.all()))
        with open('export/institutionterritories.csv', 'wb') as f:
            w = csv.DictWriter(f,
                               ['institution_id',
                                'municipality',
                                'elderate',
                                'city',
                                'street',
                                'number_from',
                                'number_to',
                                'number_filter',
                                'comment'])
            w.writeheader()
            for t in ProgressBar()(InstitutionTerritory.objects.all()):
                if t.numberOdd is None:
                    number_filter = 'all'
                elif t.numberOdd:
                    number_filter = 'odd'
                else:
                    number_filter = 'even'
                w.writerow({'institution_id': str(t.institution.id),
                            'municipality': e(t.municipality),
                            'elderate': e(t.civilParish),
                            'city': e(t.city),
                            'street': e(t.street),
                            'number_from': e(t.numberFrom),
                            'number_to': e(t.numberTo),
                            'number_filter': number_filter,
                            'comment': e(t.comment)})
