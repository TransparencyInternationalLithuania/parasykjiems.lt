# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import import_models
from web import models


class Command(BaseCommand):
    args = '<>'
    help = '''Imports articles from "data/articles.csv"'''

    def handle(self, *args, **options):
        import_models('data/articles.csv',
                      models.Article,
                      'location',
                      ['title', 'body'])
