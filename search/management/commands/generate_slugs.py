import itertools
import re
from django.core.management.base import BaseCommand
from unidecode import unidecode
from progressbar import ProgressBar, Bar, ETA

from search.models import Location
from search.multisub import multisub_all_sequential


class Command(BaseCommand):
    args = '<>'
    help = """Generates slugs for models."""

    def handle(self, *args, **options):
        def parses_as_int(s):
            try:
                x = int(s)
                return True
            except ValueError:
                return False

        print 'Generating location slugs.'
        for loc in ProgressBar(widgets=[ETA(), ' ', Bar()])(
            Location.objects.filter(slug='')):

            blob = multisub_all_sequential(
                unidecode(u' '.join([loc.street,
                                     loc.city,
                                     loc.elderate,
                                     loc.municipality])).lower(),
                (('gatve', ''),         # remove unimportant words
                 ('savivaldybe', ''),
                 ('miesto', ''),
                 ('rajono', ''),
                 ('kaimo', ''),
                 ('prospektas', ''),
                 ('miestas', ''),
                 ('kaimas', ''))
            )

            words = [re.sub(r'[^a-z0-9-]', '', word)
                     for word in blob.split(' ')]
            words = set(word            # TODO: keep word ordering
                        for word in words
                        if len(word) > 1)

            found = False
            for l in range(1, 1 + len(words)):
                for comb in itertools.combinations(words, l):
                    slug = u'-'.join(comb)
                    if (not Location.objects.filter(slug=slug).exists() and
                        not parses_as_int(slug)):
                        found = True
                        break
                if found:
                    break
            if not found:
                oldslug = slug
                for i in range(1, 10000):
                    slug = u'{}-{}'.format(oldslug, i)
                    if (not Location.objects.filter(slug=slug).exists() and
                        not parses_as_int(slug)):
                        found = True
                        break
            if not found:
                raise Exception(
                    'Unable to create unique slug for {}'.format(
                        loc))
            else:
                if '-' in slug:
                    print 'Setting slug of {} to {}'.format(loc, slug)
                loc.slug = slug
                loc.save()
