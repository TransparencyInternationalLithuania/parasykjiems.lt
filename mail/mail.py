# -*- coding: utf-8 -*-

from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.utils.translation import ugettext as _
from email.utils import formataddr, parseaddr

import settings
from parasykjiems.mail import utils
from parasykjiems.mail.models import UnconfirmedMessage, Thread, Message
from parasykjiems.slug import generate_slug
from parasykjiems.search.models import Representative

import logging
logger = logging.getLogger(__name__)


def process_incoming(envelope):
    '''Takes an incoming email envelope (email.Message object),
    inserts it into the database, tries to find a parent and
    proxy-sends the message if the parent is found.
    '''
    message = Message(
        raw_message=str(envelope).decode('utf-8'))
    message.save()
    find_parent(message)
    if message.parent:
        proxy_send(message)


def find_parent(message):
    try:
        to_name, to_email = parseaddr(message['to'])
        m = utils.MESSAGE_EMAIL_REGEXP.match(to_email)
        if m:
            id = int(m.group('id'))
            hash = int(m.group('hash'))
            maybe_parent = Message.objects.filter(id=id, reply_hash=hash)
            if maybe_parent.exists():
                message.parent = maybe_parent.get()
                message.thread = message.parent.thread
                message.save()
                # We also save the thread, so that its modification
                # date is updated.
                message.thread.save()
                logger.info(u'Parent of {} is {}.'
                            .format(message, message.parent))
    except Exception as e:
        logger.error(
            u'Exception {} while trying to determine parent of {}.'
            .format(e, message))

    if not message.parent:
        logger.warning(u'Failed to determine parent of {}.'
                       .format(message))


def proxy_send(message, recipient_name, recipient_email):
    '''Sends a Message to recipient.

    The generated envelope is designed to thread and contains the
    special reply address in the From header.
    '''
    email = EmailMessage(
        from_email=formataddr((message.sender_name, message.reply_email)),
        to=[formataddr((message.parent.sender_name,
                        message.parent.sender_email))],
        subject=message.subject,
        body=render_to_string('mail/message.txt', {
            'SETTINGS': settings,
            'body_text': message.body_text,
            'thread': message.thread,
        })
    )
    email.extra_headers = {
        'References': message.thread.references,
        'In-Reply-To': message.parent.message_id,
    }
    email.send()


def submit_message(sender_name,
                   sender_email,
                   recipient,
                   subject,
                   body_text,
                   is_open):
    """Creates an unconfirmed message with given parameters, but
    doesn't send it. Instead, sends the user a confirmation email.
    """

    message = UnconfirmedMessage(
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject,
        body_text=body_text,
        is_open=is_open,
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


def send_message(unconfirmed_message):
    """Confirms and sends the unconfirmed message. Returns the new thread.

    Creates a Thread and a Message (which contains the sent envelope).
    """

    thread = Thread(is_open=unconfirmed_message.is_open,
                    institution=unconfirmed_message.institution,
                    representative=unconfirmed_message.representative,
                    creator_name=unconfirmed_message.sender_name,
                    creator_email=unconfirmed_message.sender_email,
                    subject=unconfirmed_message.subject)
    if thread.is_open:
        generate_slug(thread,
                      Thread.objects.filter(is_open=True),
                      lambda e: [e.subject])
    thread.save()

    if settings.TESTING_VERSION:
        recipients = [formataddr((unconfirmed_message.recipient_name,
                                  settings.REDIRECT_ENQUIRIES_TO))]
    else:
        recipients = [formataddr((unconfirmed_message.recipient_name,
                                  unconfirmed_message.recipient_email))]

    message = Message(thread=thread)
    message.save()

    email = EmailMessage(
        from_email=formataddr((unconfirmed_message.sender_name,
                               message.reply_email)),
        to=recipients,
        subject=unconfirmed_message.subject,
        body=render_to_string('mail/message.txt', {
            'SETTINGS': settings,
            'body_text': unconfirmed_message.body_text,
            'thread': thread,
        }),
    )

    message.raw_message = str(email.message()).decode('utf-8')
    message.save()
    email.send()

    logger.info(u"SENT: {}".format(message))

    user_copy = EmailMessage(
        from_email=formataddr((u'ParašykJiems', settings.SERVER_EMAIL)),
        to=[formataddr((thread.creator_name, thread.creator_email))],
        subject=thread.subject,
        body=render_to_string('mail/copy.txt', {
            'message': message,
        }),
    )
    user_copy.send()

    return thread
