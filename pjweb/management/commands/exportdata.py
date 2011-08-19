import csv
import os

from django.core.management.base import BaseCommand
from progressbar import ProgressBar

from contactdb.models import InstitutionType, PersonPosition, Institution
from territories.models import InstitutionTerritory


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

        activePersonsFilter = PersonPosition.getFilterActivePositions()
        persons = PersonPosition.objects.filter(activePersonsFilter)
        print 'Exporting {} PersonPositions.'.format(
            len(persons))
        with open('export/personpositions.csv', 'wb') as f:
            w = csv.DictWriter(f,
                               ['id',
                                'name',
                                'institution_id',
                                'email',
                                'phone',
                                'other_contacts'])
            w.writeheader()
            for p in ProgressBar()(persons):
                w.writerow({'id': str(p.person.id),
                            'name': e(p.person.fullName),
                            'institution_id': str(p.institution.id),
                            'email': e(p.email),
                            'phone': e(p.primaryPhone
                                       if (p.primaryPhone and
                                           p.primaryPhone != u'')
                                       else p.secondaryPhone),
                            'other_contacts': ''})

                institutions_with_persons.add(p.institution.id)

        print 'Exporting {} Institutions.'.format(
            len(Institution.objects.all()))
        with open('export/institutions.csv', 'wb') as f:
            w = csv.DictWriter(f,
                               ['id',
                                'name',
                                'type_id',
                                'email',
                                'phone',
                                'address'])
            w.writeheader()
            for i in ProgressBar()(Institution.objects.all()):
                w.writerow({'id': str(i.id),
                            'name': e(i.name),
                            'type_id': str(i.institutionType.id),
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
