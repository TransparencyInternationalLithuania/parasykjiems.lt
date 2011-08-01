import random

from django.db import models
from django.utils.translation import ugettext_lazy as _

import search.models

_NAME_LEN = 200


class Enquiry(models.Model):
    unique_hash = models.IntegerField(db_index=True, unique=True)

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
    message_id = models.CharField(max_length=100, null=True)

    # Should be set if this message is a continuation of a discussion.
    parent = models.ForeignKey('Response', null=True)

    _hash_tries = 10
    _hash_max = 999999

    def __init__(self, *args, **kwargs):
        super(Enquiry, self).__init__(*args, **kwargs)
        if not self.unique_hash:
            self.unique_hash = random.randint(1, Enquiry._hash_max)
            tries = 0
            while Enquiry.objects.filter(unique_hash=self.unique_hash).exists():
                self.unique_hash = random.randint(1, Enquiry._hash_max)
                tries += 1
                if tries > Enquiry._hash_tries:
                    raise Exception("Probably out of unique hashes for Enquiry.")

    def recipient(self):
        return self.representative or self.institution

    @models.permalink
    def get_absolute_url(self):
        return ('letter', (), {'id': self.id})


class Response(models.Model):
    # A null parent means that it's unresolved. All responses should
    # have parents, but we might fail to find one.
    parent = models.ForeignKey(Enquiry, null=True)

    received_time = models.DateTimeField(auto_now_add=True)
    message = models.TextField(
        help_text=_("The unprocessed e-mail message."))
