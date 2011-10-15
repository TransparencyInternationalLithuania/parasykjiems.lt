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

    is_public = models.BooleanField()

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

    # We need recipient_name, so that we can display unconfirmed
    # messages with the "items/letter.html" template.
    @property
    def recipient_name(self):
        return self.recipient.name

    def __unicode__(self):
        return (u'{id}: {name} <{email}> to {to_name} (unconfirmed)'
                .format(
                    id=self.id,
                    name=self.sender_name,
                    email=self.sender_email,
                    to_name=self.recipient.name))

    class Meta:
        verbose_name = _('unconfirmed message')
        verbose_name_plural = _('unconfirmed messages')


class Message(models.Model):
    reply_hash = models.BigIntegerField(default=generate_hash,
                                        db_index=True,
                                        null=False, blank=True)

    parent = models.ForeignKey('Message', null=True)
    thread = models.ForeignKey('Thread', null=True)

    date = models.DateTimeField(auto_now_add=True)

    KIND_CHOICES = (('enquiry', _('Sent from user to representative')),
                    ('response', _('Sent from representative to user')))
    kind = models.CharField(max_length=8, choices=KIND_CHOICES)

    envelope = models.TextField(
        blank=True,
        help_text=_('If the message was received through SMTP, the '
                    'original email text.'))

    # The name and email of the *intended* recipient. This is not
    # filled from the envelope.
    recipient_name = models.CharField(max_length=_NAME_LEN, default=u'')
    recipient_email = models.CharField(max_length=_NAME_LEN, default=u'')

    # These fields can be filled automatically when the message has an
    # envelope.
    sender_name = models.CharField(max_length=_NAME_LEN)
    sender_email = models.CharField(max_length=_NAME_LEN)
    subject = models.CharField(max_length=_NAME_LEN)
    body_text = models.TextField()

    # This ID is used for filling References and In-Reply-To in
    # outgoing messages for threading on the user's side. If the
    # message is created from a web form, and therefore doesn't have a
    # Message-ID itself, this should be set to the ID of the user's
    # copy of the outgoing message.
    message_id = models.CharField(max_length=_NAME_LEN, blank=True)

    @property
    def envelope_object(self):
        """Return the corresponding email.message.Message object.
        Caches the parsed object for subsequent requests.
        """
        if not hasattr(self, '_envelope_object'):
            if self.envelope == u'':
                self._envelope_object = None
            else:
                self._envelope_object = email.message_from_string(
                    self.envelope.encode('utf-8'))
        return self._envelope_object

    def fill_from_envelope(self):
        assert(self.envelope_object)
        self.message_id = utils.decode_header_unicode(
            self.envelope_object['message-id'])
        self.sender_name = utils.extract_name(
            utils.decode_header_unicode(self.envelope_object['from']))
        self.sender_email = utils.extract_email(
            utils.decode_header_unicode(self.envelope_object['from']))
        self.subject = utils.decode_header_unicode(
            self.envelope_object['subject'])

        body_text = u''
        for part in self.envelope_object.walk():
            if part.get_content_type() == 'text/plain':
                charset = part.get_content_charset()
                body_text = part.get_payload(decode=True).decode(charset)
                break
        if body_text == u'':
            logging.warning(u"Couldn't extract body text out of {}"
                            .format(self))
        self.body_text = utils.remove_reply_email(body_text)

    @property
    def reply_email(self):
        '''The email that replies to this message should be sent to.
        '''
        return u'{prefix}+{id}.{hash}@{domain}'.format(
            prefix=settings.REPLY_EMAIL_PREFIX,
            id=self.id,
            hash=self.reply_hash,
            domain=settings.SITE_DOMAIN)

    def __unicode__(self):
        return u'{id}:{sender} -> {recipient} ({date})'.format(
            id=self.id,
            sender=self.sender_name,
            recipient=self.recipient_name,
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

    is_public = models.BooleanField(default=False)

    # These link to the institution or representative participating in
    # this thread. At most one of them should be non-null.
    institution = models.ForeignKey('search.Institution',
                                    null=True, blank=True)
    representative = models.ForeignKey('search.Representative',
                                       null=True, blank=True)

    creator_name = models.CharField(max_length=_NAME_LEN)
    creator_email = models.CharField(max_length=_NAME_LEN)

    subject = models.CharField(max_length=400)

    @property
    def recipient(self):
        return self.representative or self.institution

    @property
    def messages(self):
        return Message.objects.filter(thread=self).order_by('date')

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

    def __unicode__(self):
        return u'{id}: "{subject}" by {creator} ({date})'.format(
            id=self.id,
            subject=self.subject,
            creator=self.creator_name,
            date=self.created_at)

    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')
