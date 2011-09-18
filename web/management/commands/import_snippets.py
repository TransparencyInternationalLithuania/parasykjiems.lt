# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import import_models
from web import models


class Command(BaseCommand):
    args = '<>'
    help = '''Imports snippets from "data/snippets.csv"'''

    def handle(self, *args, **options):
        import_models('data/snippets.csv',
                      models.Snippet,
                      ['name'],
                      ['body'])
