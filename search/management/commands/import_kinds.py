# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import import_models
from search import models


class Command(BaseCommand):
    args = '<>'
    help = '''Imports kind data to "data/kinds/representative.csv" and
    "data/kinds/institution.csv"'''

    def handle(self, *args, **options):
        import_models('data/kinds/institution.csv',
                      models.InstitutionKind,
                      ['name'],
                      ['ordinal', 'description'])
        import_models('data/kinds/representative.csv',
                      models.RepresentativeKind,
                      ['name'],
                      ['ordinal', 'description'])
