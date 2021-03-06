"""This module contains mail-related models.

Both UnconfirmedMessage can be duck-typed as a Message. They both have
the properties sender_name, recipient_name, subject, date, body and
kind, which allows them to be used with the items/message.html template
passing the specific instance as the message parameter.
"""

import random
import email
import re
from unidecode import unidecode

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile
from django.core import urlresolvers

from parasykjiems.slug import SLUG_LEN
from parasykjiems.mail import utils
import settings
import antiword
from dehtml import dehtml

import logging
logger = logging.getLogger(__name__)


_NAME_LEN = 200

_RANDOM_GENERATOR = random.SystemRandom()
_SECRET_LEN = 10
_SECRET_MAX = int('9' * _SECRET_LEN)


def generate_secret():
    return str(_RANDOM_GENERATOR.randint(1, _SECRET_MAX))


class UnconfirmedMessage(models.Model):
    confirm_secret = models.CharField(default=generate_secret,
                                      max_length=_SECRET_LEN,
                                      db_index=True,
                                      null=False, blank=True)

    sender_name = models.CharField(max_length=_NAME_LEN)
    sender_email = models.EmailField(max_length=_NAME_LEN)
    subject = models.CharField(max_length=400)
    body_text = models.TextField()

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
    # messages with the "items/message.html" template.
    @property
    def recipient_name(self):
        return self.recipient.name

    @property
    def recipient_url(self):
        return self.recipient.get_absolute_url()

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


def _attachment_filesystem_name(attachment, filename):
    index = attachment.message.attachment_set.count() + 1
    return 'attachment/{}-{}-{}'.format(
        attachment.message.id,
        index,
        attachment.original_filename,
    )


class Attachment(models.Model):
    message = models.ForeignKey('Message')
    original_filename = models.CharField(max_length=200)
    mimetype = models.CharField(max_length=200)
    file = models.FileField(upload_to=_attachment_filesystem_name)

    def get_content(self):
        return self.file.read()

    def set_content(self, content):
        self.file.save(_attachment_filesystem_name(self, self.original_filename), ContentFile(content))

    def get_absolute_url(self):
        return self.file.url

    def __unicode__(self):
        return self.file.name


# Attachments with these mimetypes will be processed when received from a representative.
ATTACHMENT_MIMETYPES = frozenset([
    'application/pdf',
    'application/msword',
    'application/msexcel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.oasis.opendocument.spreadsheet',
])


class Message(models.Model):
    reply_secret = models.CharField(default=generate_secret,
                                    max_length=_SECRET_LEN,
                                    db_index=True,
                                    null=False, blank=True)

    parent = models.ForeignKey('Message', null=True, blank=True)
    thread = models.ForeignKey('Thread', null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)

    KIND_CHOICES = (('enquiry', _('Enquiry')),
                    ('response', _('Response')))
    kind = models.CharField(max_length=8, choices=KIND_CHOICES, blank=True)

    # Set if there was a problem processing this message.
    is_error = models.BooleanField(default=False)
    error_reason = models.TextField(blank=True)

    # Set when this message is proxied to the recipient.
    is_sent = models.BooleanField(default=False)

    # Set when a reply with an attachment is received. The attachment may
    # contain the reply secret, so any further replies are considered unsafe
    # and are marked as errors for further review.
    is_locked = models.BooleanField(default=False)

    envelope = models.TextField(
        blank=True,
        help_text=_('If the message was received through SMTP, the '
                    'original email text.'))

    # The name and email of the *intended* recipient. This is not
    # filled from the envelope.
    recipient_name = models.CharField(max_length=_NAME_LEN, blank=True)
    recipient_email = models.CharField(max_length=_NAME_LEN, blank=True)

    # These fields can be filled automatically when the message has an
    # envelope.
    sender_name = models.CharField(max_length=_NAME_LEN, blank=True)
    sender_email = models.CharField(max_length=_NAME_LEN, blank=True)
    subject = models.CharField(max_length=_NAME_LEN, blank=True)
    body_text = models.TextField(blank=True)

    # The message ID of the outgoing (proxied) message. Used to set the
    # in-reply-to and references headers.
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

    @property
    def sender_url(self):
        if not self.thread or self.kind == 'enquiry':
            return None
        elif (self.thread.representative and
              self.thread.representative.name == self.sender_name):
            return self.thread.representative.get_absolute_url()
        else:
            return None

    @property
    def recipient_url(self):
        if not self.thread or self.kind == 'response':
            return None
        elif (self.thread.representative and
              self.thread.representative.name == self.recipient_name):
            return self.thread.representative.get_absolute_url()
        elif self.thread.institution:
            return self.thread.institution.get_absolute_url()
        else:
            return None

    def fill_headers(self):
        assert(self.envelope_object)
        self.sender_name = utils.extract_name(
            utils.decode_header_unicode(self.envelope_object['from']))
        self.sender_email = utils.extract_email(
            utils.decode_header_unicode(self.envelope_object['from']))
        self.subject = utils.decode_header_unicode(
            self.envelope_object['subject'])

    def fill_content(self):
        assert(self.kind)
        plain_texts = []
        word_texts = []
        html_texts = []
        has_attachment = False
        for part in self.envelope_object.walk():
            if part.get_content_type() == 'message/delivery-status':
                self.save()
                raise Exception('Bounce email.'.format(self))
            elif not part.is_multipart():
                if part.get_content_type() == 'text/plain':
                    charset = part.get_content_charset()
                    payload = part.get_payload(decode=True)
                    if payload != '':
                        plain_texts.append(
                            payload.decode(charset))
                elif part.get_content_type() == 'text/html':
                    charset = part.get_content_charset()
                    payload = part.get_payload(decode=True)
                    if payload != '':
                        html_texts.append(
                            dehtml(payload.decode(charset)))
                elif self.kind == 'response':
                    # Only accept attachments from representatives.
                    if part.get_content_type() == 'application/msword':
                        word_texts.append(
                            antiword.antiword_string(
                                part.get_payload(decode=True))
                            .replace('[pic]', '')
                            .replace('|', ''))
                    if part.get_content_type() in ATTACHMENT_MIMETYPES:
                        has_attachment = True
                        attachment = Attachment(
                            mimetype=part.get_content_type(),
                            original_filename=part.get_filename(),
                            message=self,
                        )
                        attachment.set_content(part.get_payload(decode=True))
                        attachment.save()
                        self.parent.is_locked = True
                        self.parent.save()
                else:
                    logger.warning(u'Skipping attachment {} ({}) in {} {}'.format(
                        part.get_filename(),
                        part.get_content_type(),
                        self.kind,
                        self.id,
                    ))
        if not (plain_texts or html_texts or word_texts or has_attachment):
            raise Exception("Couldn't extract any content")
        body_text = '\n\n***\n\n'.join((plain_texts or html_texts) + word_texts)
        self.body_text = utils.remove_consequentive_empty_lines(
            utils.remove_reply_email(body_text))

    @property
    def reply_email(self):
        '''The email that replies to this message should be sent to.
        '''
        return u'{prefix}+{id}.{secret}@{domain}'.format(
            prefix=settings.REPLY_EMAIL_PREFIX,
            id=self.id,
            secret=self.reply_secret,
            domain=settings.SITE_DOMAIN)

    @property
    def id_in_thread(self):
        return self.thread and (list(self.thread.messages).index(self) + 1)

    def get_absolute_url(self):
        if not self.id_in_thread:
            raise Exception("Can't get URL of orphan message.")
        return '{}#message-{}'.format(
            self.thread.get_absolute_url(),
            self.id_in_thread
        )

    def get_admin_url(self):
        return settings.SITE_ADDRESS + urlresolvers.reverse('admin:mail_message_change', args=(self.id,))

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

    # These link to the institution or representative participating in
    # this thread. At most one of them should be non-null.
    institution = models.ForeignKey('search.Institution',
                                    null=True, blank=True)
    representative = models.ForeignKey('search.Representative',
                                       null=True, blank=True)

    sender_name = models.CharField(max_length=_NAME_LEN)
    sender_email = models.CharField(max_length=_NAME_LEN)

    recipient_name = models.CharField(max_length=_NAME_LEN)
    recipient_email = models.CharField(max_length=_NAME_LEN)

    subject = models.CharField(max_length=400)

    filter_keywords = models.TextField(db_index=True, blank=True)

    _WORD = re.compile(r'\w+')
    _SEARCH_TERM = re.compile(r'(?:\B-)?\w+')
    _NONWORD = re.compile(r'\W+')

    def update_filter_keywords(self):
        sources = [self.subject, self.sender_name, self.recipient_name]
        if self.institution:
            for representative in self.institution.representative_set.all():
                sources.append(representative.name)
        if self.representative:
            sources.append(self.representative.institution.name)
        words = frozenset(Thread._WORD.findall('\n'.join(unidecode(x).lower() for x in sources)))
        self.filter_keywords = ' '.join(words)

    @classmethod
    def make_filter_query(cls, q):
        """Build filter query. Words can be in any order."""

        words = Thread._SEARCH_TERM.findall(unidecode(q).lower())

        q = models.Q()
        print words
        for w in words:
            # Exclude words that start with a dash.
            negate = w.startswith('-')
            w = Thread._NONWORD.sub('', w)
            if w:
                subq = models.Q(filter_keywords__contains=w)
                if negate:
                    subq = ~subq
                q &= subq
        return q

    @property
    def recipient(self):
        return self.representative or self.institution

    @property
    def messages(self):
        return self.message_set.filter(is_error=False, is_sent=True).order_by('date')

    @property
    def has_answer(self):
        return self.message_set.filter(is_error=False, is_sent=True, kind='response').exists()

    @property
    def has_errors(self):
        return self.message_set.filter(is_error=True).exists()

    @property
    def references(self):
        return ' '.join(self.messages.exclude(message_id='').values_list('message_id', flat=True))

    @models.permalink
    def get_absolute_url(self):
        if self.slug == '':
            raise Exception('Tried to get address of object missing a slug.')
        return ('thread', [self.slug])

    def __unicode__(self):
        return (u'{id}: "{subject}" from {sender} to {recipient} ({date})'
                .format(
                    id=self.id,
                    subject=self.subject,
                    sender=self.sender_name,
                    recipient=self.recipient_name,
                    date=self.created_at))

    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')
