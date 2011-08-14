import email
import sys
from django.core.management.base import BaseCommand
from parasykjiems.mail import mail


class Command(BaseCommand):
    args = '<>'
    help = '''
    Takes a response email from stdin and inserts it into the database.
    '''

    def handle(self, *args, **options):
        msg = email.message_from_file(sys.stdin)
        mail.process_incoming(msg)