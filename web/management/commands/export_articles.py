# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import export_models
from web import models


class Command(BaseCommand):
    args = '<>'
    help = '''Exports articles to "data/articles.csv"'''

    def handle(self, *args, **options):
        export_models('data/articles.csv',
                      models.Article.objects
                      .order_by('location'),
                      ['location', 'title', 'body'])
