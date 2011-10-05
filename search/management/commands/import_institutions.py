# -*- coding: utf-8 -*-

import os

from django.core.management.base import BaseCommand
from csv_serialization import import_models
from search import models


class Command(BaseCommand):
    args = '<>'
    help = 'Imports institution data from "data/institutions/[kind].csv".'

    def handle(self, *args, **options):
        for kind in (models.InstitutionKind.objects
                     .order_by('ordinal')):
            filename = os.path.join('data',
                                    'institutions',
                                    kind.name.encode('utf-8') + '.csv')
            import_models(filename,
                          models.Institution,
                          ['name'],
                          ['email', 'phone', 'address', 'other_info'],
                          {'kind': kind})
