# -*- coding: utf-8 -*-

import os

from django.core.management.base import BaseCommand
from csv_serialization import export_models
from search import models


class Command(BaseCommand):
    args = '<>'
    help = '''
    Exports the data for all the institutions into
    "data/institutions/[kind].csv".
    '''

    def handle(self, *args, **options):
        for kind in (models.InstitutionKind.objects
                     .order_by('ordinal')):
            filename = os.path.join('data', 'institutions',
                                    kind.name.encode('utf-8') + '.csv')
            export_models(filename,
                          models.Institution.objects
                          .filter(kind=kind)
                          .order_by('name'),
                          ['name', 'email', 'phone', 'address'])
