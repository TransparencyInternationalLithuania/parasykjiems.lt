# -*- coding: utf-8 -*-

import csv
import os

from django.core.management.base import BaseCommand
from progressbar import ProgressBar
from unidecode import unidecode

from search import models


class Command(BaseCommand):
    args = '<>'
    help = '''
    Exports the data for all the institutions into
    "data/institutions/[kind].csv".
    '''

    def handle(self, *args, **options):
        def e(u):
            return u.encode('utf-8')

        d = os.path.join('data', 'institutions')
        if not os.path.exists(d):
            os.makedirs(d)

        for kind in models.InstitutionKind.objects.filter(active=True):
            filename = os.path.join(d, unidecode(kind.name)) + '.csv'
            print 'Exporting {} to "{}".'.format(e(kind.name), filename)
            with open(filename, 'wb') as f:
                w = csv.DictWriter(f,
                                   ['name',
                                    'email',
                                    'phone',
                                    'address'])
                w.writeheader()
                for i in ProgressBar()(
                    models.Institution.objects
                    .filter(kind=kind)
                    .order_by('name')):

                    w.writerow({'name': e(i.name),
                                'email': e(i.email),
                                'phone': e(i.phone),
                                'address': e(i.address)})
