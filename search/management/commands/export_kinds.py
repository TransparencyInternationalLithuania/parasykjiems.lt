# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import export_models
from search import models


class Command(BaseCommand):
    args = '<>'
    help = '''Exports kind data to "data/kinds/representative.csv" and
    "data/kinds/institution.csv"'''

    def handle(self, *args, **options):
        export_models('data/kinds/representative.csv',
                      models.RepresentativeKind.objects
                      .order_by('ordinal'),
                      ['ordinal', 'name', 'description'])
        export_models('data/kinds/institution.csv',
                      models.InstitutionKind.objects
                      .order_by('ordinal'),
                      ['ordinal', 'name', 'description'])
