# -*- coding: utf-8 -*-

from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.utils.translation import ugettext as _
from email.utils import formataddr, getaddresses

import settings
from parasykjiems.mail import utils
from parasykjiems.mail.models import UnconfirmedMessage, Thread, Message
from parasykjiems.slug import generate_slug
from parasykjiems.search.models import Representative

import traceback
import logging
logger = logging.getLogger(__name__)


def process_incoming(envelope):
    '''Takes an incoming email envelope (email.Message object),
    inserts it into the database, tries to find a parent and
    proxy-sends the message if the parent is found.
    '''
    message = Message(
        envelope=str(envelope).decode('utf-8'))
    message.save()
    process_message(message)


def process_message(message):
    try:
        message.fill_headers()
        find_parent(message)
        if not message.parent:
            raise Exception(u'Failed to determine parent.')
        if message.parent.is_locked:
            raise Exception(u'Parent thread locked.')
        message.fill_content()
        proxy_send(message)
        message.is_error = False
        message.error_reason = u''
    except Exception as e:
        trace = traceback.format_exc(e)
        message.is_error = True
        message.error_reason = trace
        message.save()
        logger.error(u'Error processing message {}\n\n{}'.format(
            message.get_admin_url(),
            trace,
        ))


def find_parent(message):
    addresses = []
    for header in ['to', 'delivered-to', 'cc', 'resent-to', 'resent-cc']:
        addresses += message.envelope_object.get_all(header, [])
    all_recipients = getaddresses(addresses)
    for to_name, to_email in all_recipients:
        m = utils.MESSAGE_EMAIL_REGEXP.match(to_email)
        if m:
            id = int(m.group('id'))
            secret = m.group('secret')
            maybe_parent = Message.objects.filter(id=id, reply_secret=secret)
            if maybe_parent.exists():
                message.parent = maybe_parent.get()
                message.recipient_name = message.parent.sender_name
                message.recipient_email = message.parent.sender_email
                message.thread = message.parent.thread
                if message.parent.kind == 'enquiry':
                    message.kind = 'response'
                else:
                    message.kind = 'enquiry'
                message.save()

                # We also save the thread, so that its modification
                # date is updated.
                message.thread.save()

                logger.info(u'PARENT of <{}> is <{}>'
                            .format(message, message.parent))

                break


def proxy_send(message):
    '''Sends a Message to recipient.

    The generated envelope is designed to thread and contains the
    special reply address in the From header.
    '''
    assert(message.recipient_email != u'')

    if message.is_sent:
        logger.warning(u'ALREADY SENT: {}'.format(message))

    email = EmailMessage(
        from_email=formataddr((message.sender_name, message.reply_email)),
        to=[formataddr((message.recipient_name, message.recipient_email))],
        subject=message.subject,
        body=render_to_string('mail/message.txt', {
            'SETTINGS': settings,
            'body_text': message.body_text,
            'thread': message.thread,
        }),
        attachments=[(a.original_filename, a.get_content(), a.mimetype)
                     for a in message.attachment_set.all()],
    )
    if message.parent:
        email.extra_headers['References'] = message.thread.references
        email.extra_headers['In-Reply-To'] = message.parent.message_id
    message.message_id = email.message()['Message-ID']
    email.extra_headers['Message-Id'] = message.message_id
    email.send()
    message.is_sent = True
    message.save()
    logger.info(u"SENT: {}".format(message))


def submit_message(sender_name, sender_email, recipient, subject, body_text):
    """Creates an unconfirmed message with given parameters, but
    doesn't send it. Instead, sends the user a confirmation email.
    """

    message = UnconfirmedMessage(
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject,
        body_text=body_text,
    )

    if isinstance(recipient, Representative):
        message.representative = recipient
    else:
        message.institution = recipient
    message.save()

    send_mail(
        from_email=formataddr((u'ParašykJiems', settings.SERVER_EMAIL)),
        recipient_list=[formataddr((sender_name, sender_email))],
        subject=_('Confirm your letter'),
        message=render_to_string('mail/confirm.txt', {
            'SETTINGS': settings,
            'message': message,
        }),
    )

    logger.info(u"SUBMIT: {}".format(message))

    return message


def confirm_and_send(unconfirmed_message):
    """Confirms and sends the unconfirmed message. Returns the new thread.

    Creates a Thread and a Message (which contains the sent envelope).
    """

    thread = Thread(institution=unconfirmed_message.institution,
                    representative=unconfirmed_message.representative,
                    sender_name=unconfirmed_message.sender_name,
                    sender_email=unconfirmed_message.sender_email,
                    recipient_name=unconfirmed_message.recipient.name,
                    recipient_email=unconfirmed_message.recipient.email,
                    subject=unconfirmed_message.subject)
    generate_slug(thread,
                  Thread.objects.all(),
                  lambda t: [t.subject])
    thread.update_filter_keywords()
    thread.save()

    message = Message(
        kind='enquiry',
        thread=thread,
        sender_name=unconfirmed_message.sender_name,
        sender_email=unconfirmed_message.sender_email,
        recipient_name=unconfirmed_message.recipient.name,
        subject=unconfirmed_message.subject,
        body_text=unconfirmed_message.body_text)
    if settings.TESTING_VERSION:
        message.recipient_email = settings.REDIRECT_ENQUIRIES_TO
    else:
        message.recipient_email = unconfirmed_message.recipient.email
    message.save()

    proxy_send(message)

    unconfirmed_message.delete()

    user_copy = EmailMessage(
        from_email=formataddr((u'ParašykJiems', settings.SERVER_EMAIL)),
        to=[formataddr((thread.sender_name, thread.sender_email))],
        subject=thread.subject,
        body=render_to_string('mail/copy.txt', {
            'message': message,
        }),
    )

    # Set the message ID of the user copy to be the same as that of the
    # outgoing message, so that when an answer is received and proxied to the
    # user, it references the user's copy for threading.
    user_copy.extra_headers['Message-ID'] = message.message_id

    user_copy.send()

    return thread

