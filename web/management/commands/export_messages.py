# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import export_models
from web import models


class Command(BaseCommand):
    args = '<>'
    help = '''Exports messages to "data/messages.csv"'''

    def handle(self, *args, **options):
        export_models(models.Message.objects
                      .order_by('name'),
                      'data/messages.csv',
                      ['name', 'body'])