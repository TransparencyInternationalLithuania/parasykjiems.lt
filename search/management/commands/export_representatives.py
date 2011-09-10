# -*- coding: utf-8 -*-

import csv
import os

from django.core.management.base import BaseCommand
from progressbar import ProgressBar

from search import models


class Command(BaseCommand):
    args = '<>'
    help = '''
    Exports all representative data to
    "data/representatives/[kind].csv".
    '''

    def handle(self, *args, **options):
        def e(u):
            return u.encode('utf-8')

        d = os.path.join('data', 'representatives')
        if not os.path.exists(d):
            os.makedirs(d)

        for kind in models.RepresentativeKind.objects.filter(active=True):
            filename = os.path.join(d, e(kind.name)) + '.csv'
            print 'Exporting {} to "{}".'.format(e(kind.name), filename)
            with open(filename, 'wb') as f:
                w = csv.DictWriter(f,
                                   ['institution',
                                    'name',
                                    'email',
                                    'phone',
                                    'other_contacts'])
                w.writeheader()
                for r in ProgressBar()(
                    models.Representative.objects
                    .filter(kind=kind)
                    .order_by('name')):

                    w.writerow({'institution': e(r.institution.name),
                                'name': e(r.name),
                                'email': e(r.email),
                                'phone': e(r.phone),
                                'other_contacts': e(r.other_contacts)})
