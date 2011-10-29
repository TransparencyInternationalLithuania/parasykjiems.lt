import datetime
from django.core.management.base import BaseCommand

import mail.models


class Command(BaseCommand):
    args = '<>'
    help = '''
    Removes unconfirmed messages that are older than two weeks.
    '''

    def handle(self, *args, **options):
        two_weeks_ago = datetime.datetime.today() - datetime.timedelta(14)
        old_messages = (mail.models.UnconfirmedMessage.objects
                        .filter(submitted_at__lt=two_weeks_ago))
        count = old_messages.count()
        old_messages.delete()
        print 'Deleted {} messages.'.format(count)
