from django.core.management.base import BaseCommand
from progressbar import ProgressBar, Bar, ETA
from search import models


class Command(BaseCommand):
    args = '<>'
    help = """Tries to tidy elderates in territories.

    Sometimes a territory is entered both an elderate and without one
    for different institutions. This command finds all instances of
    territories with missing elderates and fills them from other
    territories with exact same municipality, city and street.

    This is only done for territories without streets. For territories
    with streets, the elderate is removed altogether, because the user
    needn't know his elderate and hopefully he'll use our search to
    find his elderate by house number.
    """

    def handle(self, *args, **options):
        print 'Filling elderates.'
        count = 0
        filled = 0
        no_elderate = models.Territory.objects.filter(
            elderate='',
            street='')
        for t in ProgressBar(widgets=[ETA(), ' ', Bar()])(no_elderate):
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
        print

        print 'Removing elderates from territories with streets.'
        streets = models.Territory.objects.exclude(
            elderate='',
            street='')
        for street in ProgressBar(widgets=[ETA(), ' ', Bar()])(streets):
            street.elderate = ''
            street.save()
