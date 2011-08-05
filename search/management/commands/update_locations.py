# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from search.models import Location


class Command(BaseCommand):
    args = '<>'
    help = "Updates locations to match territories."

    def handle(self, *args, **options):
        print "Building locations."

        # A complicated SQL query is used for speed. I don't think
        # this is possible to express in Django's ORM.
        #
        # The complicated joins are meant to filter out territories of
        # inactive institutions.

        cursor = connection.cursor()
        cursor.execute('''
        DELETE FROM search_location;

        INSERT INTO search_location (municipality, elderate, city, street)
          SELECT DISTINCT municipality, elderate, city, street
          FROM
            search_territory
            INNER JOIN search_institution
              ON (search_territory.institution_id = search_institution.id)
            INNER JOIN search_institutionkind
              ON (search_institution.kind_id = search_institutionkind.id)
          WHERE search_institutionkind.active = true;
        ''')
        transaction.commit_unless_managed()

        print 'Created {} locations.'.format(Location.objects.count())
