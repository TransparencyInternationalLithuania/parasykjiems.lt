# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from csv_serialization import import_models
from search import models


class Command(BaseCommand):
    args = '<>'
    help = 'Imports representatives from "data/representatives/[kind].csv"'

    def handle(self, *args, **options):
        for kind in models.RepresentativeKind.objects.all():
            import_models(os.path.join('data', 'representatives',
                                       kind.name.encode('utf-8') + '.csv'),
                          models.Representative,
                          [('institution', 'institution__name'),
                           'name'],
                          ['email',
                           'phone',
                           'other_info'],
                          {'kind': kind})
