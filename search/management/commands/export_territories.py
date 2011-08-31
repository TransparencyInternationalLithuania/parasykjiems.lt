# -*- coding: utf-8 -*-

import csv
import os

from django.core.management.base import BaseCommand
from progressbar import ProgressBar

from search import models


class Command(BaseCommand):
    args = '<>'
    help = '''
    Exports all territory data to
    "data/territories/[municipality].csv".
    '''

    def handle(self, *args, **options):
        def e(u):
            return u.encode('utf-8')

        d = os.path.join('data', 'territories')
        if not os.path.exists(d):
            os.makedirs(d)

        municipalities = (models.Territory.objects
                          .filter(institution__kind__active=True)
                          .values_list('municipality', flat=True)
                          .distinct())

        for municipality in municipalities:
            filename = os.path.join(d, e(municipality)) + '.csv'
            print 'Exporting {} to "{}".'.format(e(municipality), filename)
            with open(filename, 'wb') as f:
                w = csv.DictWriter(f,
                                   ['institution',
                                    'elderate',
                                    'city',
                                    'street',
                                    'numbers'])
                w.writeheader()
                for t in ProgressBar()(
                    models.Territory.objects
                    .filter(municipality=municipality)
                    .order_by('institution__name')):

                    w.writerow({'institution': e(t.institution.name),
                                'elderate': e(t.elderate),
                                'city': e(t.city),
                                'street': e(t.street),
                                'numbers': e(t.numbers)})
