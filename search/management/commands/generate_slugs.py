# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from progressbar import ProgressBar, Bar, ETA

from parasykjiems.slug import generate_slug
from search.models import Institution, Representative, Location
from search import utils
from mail.models import Thread


def generate_slugs(query, part_getter):
    """Generates slugs for all objects in 'query' which don't have
    one.
    """

    lack_slugs = query.filter(slug='')
    if not lack_slugs.exists():
        return
    for obj in ProgressBar(widgets=[ETA(), ' ', Bar()])(lack_slugs):
        generate_slug(obj, query, part_getter)


class Command(BaseCommand):
    args = '<>'
    help = """Generates slugs for models."""

    def handle(self, *args, **options):
        print 'Generating slugs for:'

        print ' - Institution'

        generate_slugs(Institution.objects.all(),
                       lambda i: utils.split_institution_name(i.name))

        print ' - Representative'
        generate_slugs(Representative.objects.all(),
                       lambda r: [r.name,
                                  r.kind.name,
                                  r.institution.name])

        print ' - Location'
        generate_slugs(Location.objects.all(),
                       lambda loc: [loc.street,
                                    loc.city,
                                    loc.elderate,
                                    loc.municipality])

        print ' - Thread'
        generate_slugs(Thread.objects.all(),
                       lambda t: [t.subject])
