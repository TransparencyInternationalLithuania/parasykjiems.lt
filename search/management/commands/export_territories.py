# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from csv_serialization import export_models
from search import models
from search.municipalities import MUNICIPALITIES


class Command(BaseCommand):
    args = '<>'
    help = 'Exports territories to "data/territories/[kind].csv"'

    def handle(self, *args, **options):
        for i in xrange(len(MUNICIPALITIES)):
            municipality = MUNICIPALITIES[i]
            print '({:2}/{:2})'.format(i + 1, len(MUNICIPALITIES)),
            filename = os.path.join('data', 'territories',
                                    municipality.encode('utf-8') + '.csv')
            export_models(filename,
                          models.Territory.objects
                          .filter(municipality=municipality,
                                  institution__kind__active=True)
                          .order_by('institution__name',
                                    'elderate', 'city', 'street'),
                          [('institution', 'institution__name'),
                           'elderate',
                           'city',
                           'street',
                           'numbers'])
