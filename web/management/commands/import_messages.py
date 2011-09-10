# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from csv_serialization import import_models
from web import models


class Command(BaseCommand):
    args = '<>'
    help = '''Imports messages from "data/messages.csv"'''

    def handle(self, *args, **options):
        import_models('data/messages.csv',
                      models.Message,
                      'name',
                      ['body'])
