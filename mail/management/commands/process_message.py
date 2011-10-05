import email
import sys
from django.core.management.base import BaseCommand
from django.utils import translation

from parasykjiems.mail import mail
import settings


class Command(BaseCommand):
    args = '<>'
    help = '''
    Takes a response email from stdin and inserts it into the database.
    '''

    def handle(self, *args, **options):
        # For some reason this is needed to set the language for
        # translation strings inside the command.
        translation.activate(settings.LANGUAGE_CODE)

        msg = email.message_from_file(sys.stdin)
        mail.process_incoming(msg)
