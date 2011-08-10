# -*- coding: utf-8 -*-

import datetime
import re
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.utils.translation import ugettext as _

import settings
from parasykjiems.mail.decode_header_unicode import decode_header_unicode
from parasykjiems.mail.models import Enquiry, Response
from parasykjiems.slug import generate_slug
from parasykjiems.search.models import Representative

import logging
logger = logging.getLogger(__name__)


def submit_enquiry(sender_name,
                   sender_email,
                   recipient,
                   subject,
                   body,
                   is_open,
                   parent=None):
    """Creates an enquiry with given parameters, but doesn't send
    it. Instead, sends the user a confirmation email.
    """

    enquiry = Enquiry(
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject,
        body=body,
        is_open=is_open,
        parent=parent,
    )

    if isinstance(recipient, Representative):
        enquiry.representative = recipient
    else:
        enquiry.institution = recipient
    enquiry.save()

    # Send confirmation email.
    confirm_msg = render_to_string('mail/confirm.txt', {
        'site_address': settings.SITE_ADDRESS,
        'enquiry': enquiry,
    })

    send_mail(
        from_email=settings.SERVER_EMAIL,
        recipient_list=[u'{} <{}>'.format(sender_name, sender_email)],
        subject=_('Confirm your letter'),
        message=confirm_msg,
    )

    return enquiry


def confirm_enquiry(enquiry):
    """Sends the given enquiry to the representative.
    """

    generate_slug(enquiry,
                  Enquiry.objects.filter(is_open=True, is_sent=True),
                  lambda e: [e.subject])

    if settings.REDIRECT_ENQUIRIES:
        recipients = [u'{} <{}>'.format(enquiry.recipient.name,
                                        settings.REDIRECT_ENQUIRIES_TO)]
    else:
        recipients = [u'{} <{}>'.format(enquiry.recipient.name,
                                        enquiry.recipient.email)]

    reply_to = settings.ENQUIRY_EMAIL_FORMAT.format(
        reply_hash=enquiry.reply_hash)
    message = EmailMessage(
        from_email=settings.SERVER_EMAIL,
        subject=u'[ParašykJiems] {}'.format(enquiry.subject),
        body=render_to_string('mail/enquiry.txt', {
            'site_address': settings.SITE_ADDRESS,
            'enquiry': enquiry,
        }),
        to=recipients,
    )

    # The message.message()['Message-Id'] returns a new id every time
    # we ask for one. Here we actually set the message id in the
    # EmailMessage object, so that it is the same as the one in the
    # database when the message is sent.
    enquiry.message_id = message.message()['Message-Id']
    message.extra_headers = {
        'Message-Id': enquiry.message_id,
        'Reply-To': reply_to,
    }

    message.send()

    enquiry.is_sent = True
    enquiry.sent_at = datetime.datetime.now()

    enquiry.save()

    msg = message.message()
    user_copy = EmailMessage(
        from_email=settings.SERVER_EMAIL,
        subject=_("Copy of the letter you sent."),
        body=render_to_string('mail/copy.txt', {
            'from': decode_header_unicode(msg['from']),
            'to': decode_header_unicode(msg['to']),
            'date': decode_header_unicode(msg['date']),
            'subject': decode_header_unicode(msg['subject']),
            'body': message.message().get_payload(decode=True),
        }),
        to=[u'{} <{}>'.format(enquiry.sender_name, enquiry.sender_email)])
    user_copy.send()


def process_incoming(message):
    """Takes an email.message.Message instance and turns it into a
    Response.
    """

    response = Response(
        raw_message=str(message).decode('utf-8'))

    parent = None
    try:
        # First, try matching by 'To'.
        # By using some not-very-general hackery, we turn
        # ENQUIRY_EMAIL_FORMAT into a regexp. To be specific, we
        # escape pluses.
        r = (settings.ENQUIRY_EMAIL_FORMAT
             .replace('+', r'\+')
             .format(reply_hash='(\d+)'))
        m = re.match(r, message['to'])
        if m:
            h = int(m.group(1))
            maybe_enquiry = Enquiry.objects.filter(reply_hash=h)
            if maybe_enquiry.exists():
                logger.info('Determined parent of response {} from To.')
                parent = maybe_enquiry.get()

        # If matching by 'To' fails, try threading, though it's
        # quite unlikely that a message has an unsuitable 'To',
        # but suitable references.
        if not parent:
            refs = message['references'] or ''
            in_reply_to = message['in-reply-to'] or ''
            references = set(refs.split(' ') +
                             in_reply_to.split(' ')[0:1])
            for ref in references:
                print repr(ref.decode('utf-8').strip())
                maybe_enquiry = Enquiry.objects.filter(
                    message_id=ref.decode('utf-8').strip())
                if maybe_enquiry.exists():
                    logger.info('Determined parent of response {} from references.')
                    parent = maybe_enquiry.get()
                    break
    except Exception as e:
        logger.error(
            'Exception {} while trying to determine parent of response {}.'
            .format(e, response.id))

    if not parent:
        logger.warning('Failed to determine parent of response {}.'
                       .format(response.id))
    else:
        response.parent = parent
        send_mail(
            from_email=settings.SERVER_EMAIL,
            recipient_list=[u'{} <{}>'.format(parent.sender_name,
                                              parent.sender_email)],
            subject=_('Your enquiry has been responded to'),
            message=render_to_string('mail/responded.txt', {
                'site_address': settings.SITE_ADDRESS,
                'response': response,
                'enquiry': parent,
            })
        )

    response.save()
