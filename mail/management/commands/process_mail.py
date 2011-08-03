import email
import sys
import re

from django.core.management.base import BaseCommand

from parasykjiems.mail.models import Enquiry, Response
import settings


class Command(BaseCommand):
    args = '<>'
    help = '''
    Takes a response email from stdin and inserts it into the database.
    '''

    def handle(self, *args, **options):
        msg = email.message_from_file(sys.stdin)

        parent = None
        try:
            # First, try matching by 'To'.

            # By using some not-very-general hackery, we turn
            # ENQUIRY_EMAIL_FORMAT into a regexp. To be specific, we
            # escape pluses.
            r = (settings.ENQUIRY_EMAIL_FORMAT
                 .replace('+', r'\+')
                 .format(unique_hash='(\d+)'))
            m = re.match(r, msg['to'])

            if m:
                uh = int(m.group(1))
                maybe_enquiry = Enquiry.objects.filter(unique_hash=uh)
                if maybe_enquiry.exists():
                    parent = maybe_enquiry.get()

            # If matching by 'To' fails, try threading, though it's
            # quite unlikely that a message has an unsuitable 'To',
            # but suitable references.
            if not parent:
                refs = msg['references'] or ''
                in_reply_to = msg['in-reply-to'] or ''
                references = set(refs.split(' ') +
                                 in_reply_to.split(' ')[0:1])
                for ref in references:
                    print repr(ref.decode('utf-8').strip())
                    maybe_enquiry = Enquiry.objects.filter(
                        message_id=ref.decode('utf-8').strip())
                    if maybe_enquiry.exists():
                        parent = maybe_enquiry.get()
                        break
        except:
            pass

        response = Response(
            raw_message=str(msg).decode('utf-8'),
            parent=parent)
        response.save()
