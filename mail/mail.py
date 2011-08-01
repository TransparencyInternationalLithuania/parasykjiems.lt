import datetime
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import settings
import mail.models
import search.models


def submit_enquiry(sender_name,
                   sender_email,
                   recipient,
                   subject,
                   body,
                   is_open=False,
                   parent=None):
    """Creates an enquiry with given parameters, but doesn't send
    it. Instead, sends the user a confirmation email.
    """

    enquiry = mail.models.Enquiry(
        from_name=sender_name,
        from_email=sender_email,
        subject=subject,
        body=body,
        is_open=is_open,
        parent=parent,
    )
    if isinstance(recipient, search.models.Representative):
        enquiry.representative = recipient
    else:
        enquiry.institution = recipient
    enquiry.save()

    # Send confirmation email.
    confirm_msg = render_to_string('mail/confirm.txt', {
        'confirm_url': reverse('confirm', [enquiry.unique_hash]),
        'sender_name': sender_name,
        'recipient': recipient,
        'subject': subject,
    })
    send_mail(
        from_email=settings.SERVER_EMAIL,
        recipient_list=[u'{} <{}>'.format(sender_name, sender_email)],
        subject=_('Confirm your enquiry'),
        message=confirm_msg,
    )

    return enquiry


def confirm_enquiry(enquiry):
    """Sends the given enquiry to the representative.
    """

    if settings.DEBUG:
        recipients = [email for name, email in settings.ADMINS]
    else:
        recipient = enquiry.institution or enquiry.representative
        recipients = [u'{} <{}>'.format(recipient.name, recipient.email)]

    reply_to = settings.ENQUIRY_EMAIL_FORMAT.format(
        unique_hash=enquiry.unique_hash)
    message = EmailMessage(
        from_email=settings.SERVER_EMAIL,
        subject=enquiry.subject,
        message=render_to_string('mail/enquiry.txt', {'enquiry': enquiry}),
        recipient_list=recipients,
        headers={'Reply-To': reply_to},
    )
    enquiry.message_id = message.message()['Message-Id']
    message.send()
    enquiry.is_sent = True
    enquiry.sent_at = datetime.datetime.now()
