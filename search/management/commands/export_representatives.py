# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from csv_serialization import export_models
from search import models


class Command(BaseCommand):
    args = '<>'
    help = 'Exports representatives from "data/representatives/[kind].csv"'

    def handle(self, *args, **options):
        for kind in models.RepresentativeKind.objects.filter(active=True):
            export_models(os.path.join('data', 'representatives',
                                       kind.name.encode('utf-8') + '.csv'),
                          models.Representative.objects
                          .filter(kind=kind)
                          .order_by('institution__name'),
                          [('institution', 'institution__name'),
                           'name',
                           'email',
                           'phone',
                           'other_contacts'])
