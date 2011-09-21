# -*- coding: utf-8 -*-

import re
from django.core.management.base import BaseCommand
from progressbar import ProgressBar, Bar, ETA

from parasykjiems.slug import generate_slug
from search.models import Institution, Representative, Location
from mail.models import Enquiry


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

        def split_institution_name(name):
            m = re.match(ur'(.+savivaldybė) (.+)', name)
            if m:
                return [m.group(2), m.group(1)]
            else:
                return [name]

        generate_slugs(Institution.objects.all(),
                       lambda i: split_institution_name(i.name))

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

        print ' - Enquiry'
        generate_slugs(Enquiry.objects
                       .filter(is_open=True, is_sent=True, parent=None),
                       lambda e: [e.subject])
