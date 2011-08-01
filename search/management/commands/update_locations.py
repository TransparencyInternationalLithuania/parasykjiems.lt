# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    args = '<>'
    help = "Updates locations to match territories."

    def handle(self, *args, **options):
        cursor = connection.cursor()

        # Data modifying operation - commit required
        cursor.execute('''
        DELETE FROM search_location;
        INSERT INTO search_location (municipality, elderate, city, street)
        SELECT DISTINCT municipality, elderate, city, street
        FROM search_territory;
        ''')
        transaction.commit_unless_managed()
