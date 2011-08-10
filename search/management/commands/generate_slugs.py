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

        generate_slugs(Enquiry.objects.filter(is_open=True),
                       lambda e: [e.subject])
