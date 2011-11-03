import datetime
from django.core.management.base import BaseCommand

import mail.models


import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<>'
    help = '''
    Removes unconfirmed messages that are older than two weeks.
    '''

    def handle(self, *args, **options):
        two_weeks_ago = datetime.datetime.today() - datetime.timedelta(14)
        old_messages = (mail.models.UnconfirmedMessage.objects
                        .filter(submitted_at__lt=two_weeks_ago))
        for message in old_messages:
            logger.info(u'PURGE {}'.format(message))
            message.delete()
