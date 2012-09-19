from django.core.management.base import BaseCommand

from mail.models import Message
from mail.mail import proxy_send


class Command(BaseCommand):
    args = '<>'
    help = '''
    Sends messages that aren't errors, but aren't sent yet.
    '''

    def handle(self, *args, **options):
        for message in Message.objects.filter(is_sent=False, is_error=False):
            proxy_send(message)
