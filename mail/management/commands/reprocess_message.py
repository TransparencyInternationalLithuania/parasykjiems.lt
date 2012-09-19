import email
import sys
import os
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from parasykjiems.mail.models import Message
from parasykjiems.mail import mail
import settings


class Command(BaseCommand):
    args = '<id>'
    help = '''
    Tries to process message with given id if it wasn't sent yet.
    '''

    def handle(self, id, **options):
        # For some reason this is needed to set the language for
        # translation strings inside the command.
        translation.activate(settings.LANGUAGE_CODE)

        # Ensure that the umask allows world-read so that attachments can be
        # read by the web server.
        os.umask(0022)

        message = Message.objects.get(id=id)
        if message.is_sent:
            raise CommandError('Message {} has already been sent.'.format(message))
        else:
            mail.process_message(message)
