"""This module contains mail-related models.

Both Enquiry and Response can be duck-typed as a letter. They both
have the properties sender_name, recipient_name, subject, date, body
and kind, which allows them to be used with the items/letter.html
template passing the specific instance as the letter parameter.
"""

import random
import email
import datetime
import time

from django.db import models
from django.utils.translation import ugettext_lazy as _

from parasykjiems.slug import SLUG_LEN
from parasykjiems.mail import utils
import settings


_NAME_LEN = 200

_RANDOM_GENERATOR = random.SystemRandom()
_HASH_MAX = 999999


def generate_hash():
    return _RANDOM_GENERATOR.randint(1, _HASH_MAX)


class Enquiry(models.Model):
    # Should be set if this message is a continuation of a discussion.
    parent = models.ForeignKey('Response', null=True, blank=True)

    # Secret hashes are separate for confirmation and replies, so that
    # a sender can't reply to himself.
    reply_hash = models.IntegerField(default=generate_hash,
                                     db_index=True,
                                     null=False, blank=True)
    confirm_hash = models.IntegerField(default=generate_hash,
                                       db_index=True,
                                       null=False, blank=True)

    slug = models.CharField(max_length=SLUG_LEN,
                            blank=True,
                            db_index=True)

    # These link to the institution or representative that this
    # enquiry was sent to. Exactly one of them should be non-null.
    institution = models.ForeignKey('search.Institution',
                                    null=True, blank=True)
    representative = models.ForeignKey('search.Representative',
                                       null=True, blank=True)

    # This should be set to the name and email of the institution or
    # representative on creation. In case, the representative's name
    # changes in the database, we still know to whom the letter was
    # sent.
    recipient_name = models.CharField(max_length=_NAME_LEN)
    recipient_email = models.CharField(max_length=_NAME_LEN)

    sender_name = models.CharField(max_length=_NAME_LEN)
    sender_email = models.EmailField(max_length=_NAME_LEN)
    subject = models.CharField(max_length=400)
    body = models.TextField()

    is_open = models.BooleanField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    is_confirmed = models.BooleanField()

    is_sent = models.BooleanField()
    sent_at = models.DateTimeField(null=True, blank=True)

    # This can be used for threading. Should be set after sending.
    message_id = models.CharField(max_length=100,
                                  null=True, blank=True,
                                  db_index=True)

    @property
    def recipient(self):
        return self.representative or self.institution

    @property
    def is_recipient_current(self):
        '''True if the recipient to whom this message was sent
        (determined by recipient_name) is the one returned by the
        recipient property.
        '''
        return (self.recipient and
                (self.recipient_name == self.recipient.name))

    @property
    def has_answer(self):
        return Response.objects.filter(parent=self.id).exists()

    @property
    def date(self):
        return self.sent_at

    @property
    def kind(self):
        return 'enquiry'

    @models.permalink
    def get_absolute_url(self):
        return ('thread', (), {'slug': self.slug})

    def __unicode__(self):
        if self.is_sent:
            sent_msg = u'sent at {}'.format(self.sent_at)
        elif self.is_confirmed:
            sent_msg = u'confirmed'
        else:
            sent_msg = u'unconfirmed'
        return u'{id}: {name} <{email}> to {to} ({sent})'.format(
            id=self.id,
            name=self.sender_name,
            email=self.sender_email,
            to=self.recipient,
            sent=sent_msg)

    class Meta:
        verbose_name = _('enquiry')
        verbose_name_plural = _('enquiries')


class Response(models.Model):
    # A null parent means that it's unresolved. All responses should
    # have parents, but we might fail to find one.
    parent = models.ForeignKey(Enquiry, null=True)

    received_time = models.DateTimeField(auto_now_add=True)
    raw_message = models.TextField(
        help_text=_("The unprocessed e-mail message."))

    @property
    def message(self):
        """Returns this Response as an email.message.Message object.

        Caches the parsed object for subsequent requests.
        """
        if not self._message:
            self._message = email.message_from_string(
                self.raw_message.encode('utf-8'))
        return self._message

    @property
    def sender_name(self):
        return utils.extract_name(
            utils.decode_header_unicode(self.message['from']))

    @property
    def recipient_name(self):
        return self.parent.sender_name

    @property
    def subject(self):
        return utils.decode_header_unicode(self.message['subject'])

    @property
    def date(self):
        return datetime.datetime.fromtimestamp(
            time.mktime(
                email.utils.parsedate(
                    self.message['date'])))

    @property
    def body(self):
        body = self.message.get_payload(decode=True)
        body = utils.ENQUIRY_EMAIL_REGEXP.sub("...@" + settings.MAIL_DOMAIN,
                                              body)
        return body

    @property
    def kind(self):
        return 'response'

    def __init__(self, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self._message = None

    def __unicode__(self):
        return u'{id}:{sender} ({received_time})'.format(
            id=self.id,
            sender=utils.decode_header_unicode(
                self.message['from']),
            received_time=self.received_time)

    class Meta:
        verbose_name = _('response')
        verbose_name_plural = _('responses')
