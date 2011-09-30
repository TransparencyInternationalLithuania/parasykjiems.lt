# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from search.models import Location


class Command(BaseCommand):
    args = '<>'
    help = "Updates locations to match territories."

    def handle(self, *args, **options):
        # A complicated SQL query is used for speed. I don't think
        # this is possible to express in Django's ORM.
        #
        # The complicated joins are meant to filter out territories of
        # inactive institutions.

        print 'Before: {} locations.'.format(Location.objects.count())

        cursor = connection.cursor()

        print 'Inserting new ones.'
        cursor.execute('''
        INSERT INTO search_location (municipality, elderate, city, street, slug)
          SELECT DISTINCT ON (upper(municipality), upper(elderate), upper(city), upper(street))
            municipality, elderate, city, street, ''
          FROM
            search_territory
            INNER JOIN search_institution
              ON (search_territory.institution_id = search_institution.id)
            INNER JOIN search_institutionkind
              ON (search_institution.kind_id = search_institutionkind.id)
          WHERE (street IS NOT NULL) OR (city IS NOT NULL)
          AND NOT EXISTS
            (SELECT *
             FROM search_location
             WHERE upper(search_location.municipality) = upper(search_territory.municipality)
               AND upper(search_location.elderate) = upper(search_territory.elderate)
               AND upper(search_location.city) = upper(search_territory.city)
               AND upper(search_location.street) = upper(search_territory.street));
        ''')
        transaction.commit_unless_managed()

        print 'Deleting old ones.'
        cursor.execute('''
        DELETE FROM search_location
        WHERE NOT EXISTS
          (SELECT *
           FROM search_territory
           WHERE upper(search_location.municipality) = upper(search_territory.municipality)
             AND upper(search_location.elderate) = upper(search_territory.elderate)
             AND upper(search_location.city) = upper(search_territory.city)
             AND upper(search_location.street) = upper(search_territory.street));
        ''')

        transaction.commit_unless_managed()

        print 'After: {} locations.'.format(Location.objects.count())
