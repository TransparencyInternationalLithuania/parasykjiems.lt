# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    args = '<>'
    help = 'Deletes all search models.'

    def handle(self, *args, **options):
        call_command('import_kinds')
        call_command('import_institutions')
        call_command('import_representatives')
        call_command('import_territories')
