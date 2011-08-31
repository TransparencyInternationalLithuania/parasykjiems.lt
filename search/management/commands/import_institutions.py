# -*- coding: utf-8 -*-

import csv
import os

from django.core.management.base import BaseCommand
from progressbar import ProgressBar, ETA, Bar
from unidecode import unidecode

from search import models


class Command(BaseCommand):
    args = '<>'
    help = 'Imports institution data from "data/institutions/[kind].csv".'

    def handle(self, *args, **options):
        def d(s):
            return s.decode('utf-8').strip()

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

        for kind in models.InstitutionKind.objects.filter(active=True):
            filename = os.path.join('data',
                                    'institutions',
                                    unidecode(kind.name)) + '.csv'
            for row in progressreader(filename):
                maybe_inst = models.Institution.objects.filter(
                    name=d(row['name']),
                    kind=kind)
                if maybe_inst.exists():
                    inst = maybe_inst.get()
                    inst.email = d(row['email'])
                    inst.phone = d(row['phone'])
                    inst.address = d(row['address'])
                    inst.save()
                else:
                    print 'Creating {}.'.format(d(row['name']))
                    models.Institution(
                        name=d(row['name']),
                        kind=kind,
                        email=d(row['email']),
                        phone=d(row['phone']),
                        address=d(row['address']),
                    ).save()
