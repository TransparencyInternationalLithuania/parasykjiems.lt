# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand
from csv_serialization import import_models
from search import models
from search.municipalities import MUNICIPALITIES


class Command(BaseCommand):
    args = '<>'
    help = 'Imports territories from "data/territories/[kind].csv"'

    def handle(self, *args, **options):
        for i in xrange(len(MUNICIPALITIES)):
            municipality = MUNICIPALITIES[i]
            print '({:2}/{:2})'.format(i + 1, len(MUNICIPALITIES)),
            filename = os.path.join('data', 'territories',
                                    municipality.encode('utf-8') + '.csv')

            # Delete all territories for this municipality before
            # importing, so that they don't double. We can't really
            # update them in any other way.
            models.Territory.objects.filter(municipality=municipality).delete()

            import_models(filename,
                          models.Territory,
                          [('institution', 'institution__name'),
                           'elderate',
                           'city',
                           'street'],
                          ['numbers'],
                          {'municipality': municipality})
