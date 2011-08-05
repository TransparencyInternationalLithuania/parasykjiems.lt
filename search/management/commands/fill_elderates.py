from django.core.management.base import BaseCommand
from search import models


class Command(BaseCommand):
    args = '<>'
    help = """Tries to fill empty elderate fields in territories.

    Sometimes a street is entered both an elderate and without one for
    different institutions. This command finds all instances of
    territories with missing elderates and fills them from other
    territories with exact same municipality, city and street.
    """

    def handle(self, *args, **options):
        no_elderate = models.Territory.objects.filter(elderate='')
        count = 0
        filled = 0
        for t in no_elderate:
            count += 1
            same_location = (models.Territory.objects
                             .filter(
                                 municipality=t.municipality,
                                 city=t.city,
                                 street=t.street)
                             .exclude(
                                 elderate=''))
            if same_location.exists():
                filled += 1
                u = same_location[0]
                print u'Setting elderate of {} to {}'.format(
                    t, u.elderate)
                t.elderate = u.elderate
                t.save()
        print 'Filled {} elderates of {} territories missing an elderate.' \
              .format(filled, count)
