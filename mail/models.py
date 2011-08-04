import random
import email

from django.db import models
from django.utils.translation import ugettext_lazy as _

import search.models

_NAME_LEN = 200


class Enquiry(models.Model):
    # Secret hashes are separate for confirmation and replies, so that
    # a sender can't reply to himself.
    confirm_hash = models.IntegerField(db_index=True, unique=True)
    reply_hash = models.IntegerField(db_index=True, unique=True)

    # These link to the institution or representative that this
    # enquiry was sent to. Exactly one of them should be non-null.
    institution = models.ForeignKey(search.models.Institution,
                                    null=True)
    representative = models.ForeignKey(search.models.Representative,
                                       null=True)

    sender_name = models.CharField(max_length=_NAME_LEN)
    sender_email = models.EmailField(max_length=_NAME_LEN)
    subject = models.CharField(max_length=400)
    body = models.TextField()

    is_open = models.BooleanField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    is_sent = models.BooleanField()
    sent_at = models.DateTimeField(null=True)

    # This can be used for threading. Should be set after sending.
    message_id = models.CharField(max_length=100, null=True, db_index=True)

    # Should be set if this message is a continuation of a discussion.
    parent = models.ForeignKey('Response', null=True)

    _hash_tries = 10
    _hash_max = 9999999

    def __init__(self, *args, **kwargs):
        super(Enquiry, self).__init__(*args, **kwargs)

        # Ensure unique confirm and reply hashes.

        rand = random.SystemRandom()

        if not self.confirm_hash:
            self.confirm_hash = rand.randint(1, Enquiry._hash_max)
            tries = 0
            while Enquiry.objects.filter(confirm_hash=self.confirm_hash).exists():
                self.confirm_hash = rand.randint(1, Enquiry._hash_max)
                tries += 1
                if tries > Enquiry._hash_tries:
                    raise Exception("Probably out of confirm hashes for Enquiry.")
        if not self.reply_hash:
            self.reply_hash = rand.randint(1, Enquiry._hash_max)
            tries = 0
            while Enquiry.objects.filter(reply_hash=self.reply_hash).exists():
                self.reply_hash = rand.randint(1, Enquiry._hash_max)
                tries += 1
                if tries > Enquiry._hash_tries:
                    raise Exception("Probably out of reply hashes for Enquiry.")

    def recipient(self):
        return self.representative or self.institution

    def has_answer(self):
        return Response.objects.filter(parent=self.id).exists()

    @models.permalink
    def get_absolute_url(self):
        return ('letter', (), {'id': self.id})

    def __unicode__(self):
        if self.is_sent:
            sent_msg = u'sent at {}'.format(self.sent_at)
        else:
            sent_msg = u'unconfirmed'
        return u'{name} <{email}> to {to} ({sent})'.format(
            name=self.sender_name,
            email=self.sender_email,
            to=self.recipient(),
            sent=sent_msg)


class Response(models.Model):
    # A null parent means that it's unresolved. All responses should
    # have parents, but we might fail to find one.
    parent = models.ForeignKey(Enquiry, null=True)

    received_time = models.DateTimeField(auto_now_add=True)
    raw_message = models.TextField(
        help_text=_("The unprocessed e-mail message."))

    def message(self):
        """Returns this Response as an email.message.Message object.
        """
        return email.message_from_string(self.raw_message.encode('utf-8'))

    def __unicode__(self):
        return u'{sender} ({received_time})'.format(
            sender=self.message()['from'],
            received_time=self.received_time)
