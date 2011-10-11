"""This module contains mail-related models.

Both Enquiry and Response can be duck-typed as a letter. They both
have the properties sender_name, recipient_name, subject, date, body
and kind, which allows them to be used with the items/letter.html
template passing the specific instance as the letter parameter.
"""

import random
import email

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parasykjiems.slug import SLUG_LEN
from parasykjiems.mail import utils
import settings

import logging
logger = logging.getLogger(__name__)


_NAME_LEN = 200

_RANDOM_GENERATOR = random.SystemRandom()
_HASH_MAX = int('9' * 10)


def generate_hash():
    return _RANDOM_GENERATOR.randint(1, _HASH_MAX)


class UnconfirmedMessage(models.Model):
    confirm_hash = models.BigIntegerField(default=generate_hash,
                                          db_index=True,
                                          null=False, blank=True)

    sender_name = models.CharField(max_length=_NAME_LEN)
    sender_email = models.EmailField(max_length=_NAME_LEN)
    subject = models.CharField(max_length=400)
    body_text = models.TextField()

    is_open = models.BooleanField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    # These link to the institution or representative participating in
    # this thread. At most one of them should be non-null.
    institution = models.ForeignKey('search.Institution',
                                    null=True, blank=True)
    representative = models.ForeignKey('search.Representative',
                                       null=True, blank=True)

    @property
    def recipient(self):
        return self.representative or self.institution

    @property
    def recipient_name(self):
        return self.recipient.name

    def __unicode__(self):
        return (u'Unconfirmed {id}: {name} <{email}> to {to_name} {to_email}'
                .format(
                    id=self.id,
                    name=self.sender_name,
                    email=self.sender_email,
                    to_name=self.recipient.name,
                    to_email=self.recipient.email))

    class Meta:
        verbose_name = _('unconfirmed message')
        verbose_name_plural = _('unconfirmed messages')


class Message(models.Model):
    reply_hash = models.BigIntegerField(default=generate_hash,
                                        db_index=True,
                                        null=False, blank=True)

    parent = models.ForeignKey('Message', null=True)
    thread = models.ForeignKey('Thread', null=True)

    date_received = models.DateTimeField(auto_now_add=True)

    raw_message = models.TextField(
        help_text=_("The unprocessed e-mail message."))

    is_replied_to = models.BooleanField(default=False)

    @property
    def message(self):
        """Return the corresponding email.message.Message object.

        Caches the parsed object for subsequent requests.
        """
        if not self._message:
            self._message = email.message_from_string(
                self.raw_message.encode('utf-8'))
        return self._message

    @property
    def message_id(self):
        return utils.decode_header_unicode(self.message['message-id'])

    @property
    def sender_name(self):
        return utils.extract_name(
            utils.decode_header_unicode(self.message['from']))

    @property
    def sender_email(self):
        return utils.extract_email(
            utils.decode_header_unicode(self.message['from']))

    @property
    def recipient_name(self):
        return utils.extract_name(
            utils.decode_header_unicode(self.message['to']))

    @property
    def recipient_email(self):
        return utils.extract_email(
            utils.decode_header_unicode(self.message['to']))

    @property
    def subject(self):
        return utils.decode_header_unicode(self.message['subject'])

    @property
    def date(self):
        return utils.decode_date_header(self.message['date'])

    @property
    def body_text(self):
        body_text = None
        for part in self.message.walk():
            if part.get_content_type() == 'text/plain':
                charset = part.get_content_charset()
                body_text = part.get_payload(decode=True).decode(charset)
                break
        if not body_text:
            logging.warning(u"Couldn't extract body text out of {}"
                            .format(self))
            body_text = u''
        body_text = utils.remove_reply_email(body_text)
        return body_text

    @property
    def reply_email(self):
        return u'{prefix}+{id}.{hash}@{domain}'.format(
            prefix=settings.REPLY_EMAIL_PREFIX,
            id=self.id,
            hash=self.reply_hash,
            domain=settings.SITE_DOMAIN)

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self._message = None

    def __unicode__(self):
        return u'{id}:{sender} -> {recipient} ({date})'.format(
            id=self.id,
            sender=utils.decode_header_unicode(
                self.message['from']),
            recipient=utils.decode_header_unicode(
                self.message['to']),
            date=self.date)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')


class Thread(models.Model):
    slug = models.CharField(max_length=SLUG_LEN,
                            blank=True,
                            db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_open = models.BooleanField(default=False)

    # These link to the institution or representative participating in
    # this thread. At most one of them should be non-null.
    institution = models.ForeignKey('search.Institution',
                                    null=True, blank=True)
    representative = models.ForeignKey('search.Representative',
                                       null=True, blank=True)

    subject = models.CharField(max_length=400)

    @property
    def recipient(self):
        return self.representative or self.institution

    @property
    def messages(self):
        return Message.objects.filter(thread=self).order_by('date_received')

    @property
    def has_answer(self):
        return self.messages.count() > 1

    @property
    def references(self):
        return ' '.join([m.message_id for m in self.messages])

    @models.permalink
    def get_absolute_url(self):
        if self.slug == '':
            raise Exception('Tried to get address of object missing a slug.')
        return ('thread', [self.slug])

    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')
