# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from search import models


class Command(BaseCommand):
    args = '<>'
    help = 'Deletes all search models.'

    def handle(self, *args, **options):
        for model in ["Territory",
                      "Location",
                      "Representative",
                      "RepresentativeKind",
                      "Institution",
                      "InstitutionKind"]:
            print 'Clearing {}.'.format(model)
            getattr(models, model).objects.all().delete()
