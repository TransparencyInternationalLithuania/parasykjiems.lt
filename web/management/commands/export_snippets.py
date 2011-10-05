# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import export_models
from web import models


class Command(BaseCommand):
    args = '<>'
    help = '''Exports snippets to "data/snippets.csv"'''

    def handle(self, *args, **options):
        export_models('data/snippets.csv',
                      models.Snippet.objects
                      .order_by('name'),
                      ['name', 'body'])
