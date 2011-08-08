import itertools
import re
from django.core.management.base import BaseCommand
from unidecode import unidecode
from progressbar import ProgressBar, Bar, ETA

from search.models import Institution, Representative, Location, SLUG_LEN
from search.multisub import multisub_all_sequential


def parses_as_int(s):
    """Determines if it possible to parse given string as an integer.
    """
    try:
        x = int(s)
        return True
    except ValueError:
        return False


def strip_dashes(s):
    """Removes dashes from the start and end of string.
    """
    return re.sub(r'^-+|-+$', '', s)


def generate_slug(obj, query, part_getter):
    """Generates slug for 'object'.

    Checks if no other object in 'query' has that slug and tries to
    uniquify it.

    'part_getter' should be a function that takes an object and
    returns a list of possible strings to be used as parts of a slug,
    in order of decreasing importance.
    """
    parts = [multisub_all_sequential(unidecode(p).lower().strip(),
                                     ((r' +', '-'),
                                      (r'[^a-z0-9-]', '')))
             for p in part_getter(obj)]
    parts = [p for p in parts if p != '']
    found = False
    for l in range(1, 1 + len(parts)):
        slug = strip_dashes(u'-'.join(parts[:l])[:SLUG_LEN])
        if (not query.filter(slug=slug).exists() and
            not parses_as_int(slug)):
            found = True
            break
    if not found:
        oldslug = slug
        for i in range(1, 10000):
            s_len = SLUG_LEN - len(u'{}'.format(i)) - 1
            slug = strip_dashes(
                u'{}-{}'.format(oldslug[:s_len], i))
            if (not query.filter(slug=slug).exists() and
                not parses_as_int(slug)):
                found = True
                break
    if not found:
        raise Exception(
            'Unable to create unique slug for {}'.format(
                obj))
    else:
        if '-' in slug:
            print 'Setting slug of {} to {}'.format(obj, slug)
        obj.slug = slug
        obj.save()


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
        generate_slugs(Institution.objects.filter(kind__active=True),
                       lambda i: [i.name,
                                  i.kind.name])

        generate_slugs(Representative.objects.filter(kind__active=True),
                       lambda r: [r.name,
                                  r.kind.name,
                                  r.institution.name])

        generate_slugs(Location.objects.all(),
                       lambda loc: [loc.street,
                                    loc.city,
                                    loc.elderate,
                                    loc.municipality])
