# -*- coding: utf-8 -*-

import datetime
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.utils.translation import ugettext as _
from email.utils import formataddr

import settings
from parasykjiems.mail import utils
from parasykjiems.mail.models import UnconfirmedMessage, Thread, Message
from parasykjiems.slug import generate_slug
from parasykjiems.search.models import Representative

import logging
logger = logging.getLogger(__name__)


def submit_message(sender_name,
                   sender_email,
                   recipient,
                   subject,
                   body,
                   is_open,
                   parent=None):
    """Creates an message with given parameters, but doesn't send
    it. Instead, sends the user a confirmation email.
    """

    message = UnconfirmedMessage(
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject,
        body=body,
        is_open=is_open,
        parent=parent,
    )

    if isinstance(recipient, Representative):
        message.representative = recipient
    else:
        message.institution = recipient
    message.save()

    # Send confirmation email.
    confirm_msg = render_to_string('mail/confirm.txt', {
        'SETTINGS': settings,
        'message': message,
    })

    send_mail(
        from_email=formataddr((u'ParašykJiems', settings.SERVER_EMAIL)),
        recipient_list=[formataddr((sender_name, sender_email))],
        subject=_('Confirm your letter'),
        message=confirm_msg,
    )

    logger.info(u"SUBMIT: {}".format(message))

    return message


def send_message(unconfirmed_message):
    """Sends the given message to the representative.
    """

    thread = Thread(is_open=unconfirmed_message.is_open,
                    institution=unconfirmed_message.institution,
                    representative=unconfirmed_message.representative,
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

    reply_addr = u'{prefix}+{id}.{hash}@{domain}'.format(
        prefix=settings.REPLY_EMAIL_PREFIX,
        id=message.id,
        hash=message.reply_hash,
        domain=settings.SITE_DOMAIN)
    email_message = EmailMessage(
        from_email=formataddr((unconfirmed_message.sender_name, reply_addr)),
        subject=unconfirmed_message.subject,
        body=render_to_string('mail/message.txt', {
            'SETTINGS': settings,
            'message': unconfirmed_message,
            'thread': thread,
        }),
        to=recipients,
    )

    # The message.message()['Message-Id'] returns a new id every time
    # we ask for one. Here we actually set the message id in the
    # EmailMessage object, so that it is the same as the one in the
    # database when the message is sent.
    email_message.message_id = email_message.message()['Message-Id']
    email_message.extra_headers = {
        'Message-Id': message.message_id,
        'Reply-To': reply_addr,
    }

    message.raw_message = str(email_message.message()).decode('utf-8')
    message.save()
    email_message.send()

    logger.info(u"SENT: {}".format(message))

    msg = email_message.message()
    user_copy = EmailMessage(
        from_email=formataddr((u'ParašykJiems', settings.SERVER_EMAIL)),
        subject=_("Copy of the letter you sent."),
        body=render_to_string('mail/copy.txt', {
            'to': utils.decode_header_unicode(msg['to']),
            'date': utils.decode_date_header(msg['date']),
            'subject': utils.decode_header_unicode(msg['subject']),
            'body': message.message().get_payload(decode=True),
        }),
        to=[formataddr((message.sender_name, message.sender_email))])
    user_copy.send()

    # TODO: continue implementing new mail system


def send_message_reply_notification(response):
    send_mail(
        from_email=formataddr((u'ParašykJiems', settings.SERVER_EMAIL)),
        recipient_list=[formataddr((response.parent.sender_name,
                                    response.parent.sender_email))],
        subject=_('Your message has been responded to'),
        message=render_to_string('mail/responded.txt', {
            'SETTINGS': settings,
            'response': response,
            'message': response.parent,
        })
    )
    response.sent_reply_notification = True
    response.save()


def process_incoming(message):
    """Takes an email.message.Message instance and turns it into a
    Response.
    """

    response = Response(
        raw_message=str(message).decode('utf-8'))
    response.save()

    parent = None
    try:
        # First, try matching by 'To'.
        m = utils.MESSAGE_EMAIL_REGEXP.match(message['to'])
        if m:
            id = int(m.group('id'))
            hash = int(m.group('hash'))
            maybe_message = Message.objects.filter(id=id, reply_hash=hash)
            if maybe_message.exists():
                logger.info(u'Determined parent of response {} from To.'
                            .format(response))
                parent = maybe_message.get()

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
                maybe_message = Message.objects.filter(
                    message_id=ref.decode('utf-8').strip())
                if maybe_message.exists():
                    logger.info(
                        u'Determined parent of response {} from references.'
                        .format(response))
                    parent = maybe_message.get()
                    break
    except Exception as e:
        logger.error(
            u'Exception {} while trying to determine parent of response {}.'
            .format(e, response))

    if not parent:
        logger.warning(u'Failed to determine parent of response {}.'
                       .format(response))
    else:
        response.parent = parent
        response.save()
        send_message_reply_notification(response)
