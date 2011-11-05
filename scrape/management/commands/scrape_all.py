# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    args = '<>'
    help = 'Runs all available scrapers.'

    def handle(self, *args, **options):
        call_command('import_vilnius')
        call_command('import_kaunas')
