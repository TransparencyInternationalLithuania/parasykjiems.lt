# -*- coding: utf-8 -*-
"""Email-related utility functions.
"""

import re
from email.header import decode_header
import email.utils
import datetime

import settings
from multisub import multisub_one
import search.models

import logging
logger = logging.getLogger(__name__)


def extract_name(email_string):
    """Take an email address string and try to extract a name (but not
    the actual address) out of it.
    """
    realname, email_addr = email.utils.parseaddr(email_string)
    if realname == u'':
        realname = email_addr[0:email_addr.find('@')]
    if realname == u'':
        logger.warning("Can't extract name from email '{}'.".format(
            email_string))
    return realname


def extract_email(email_string):
    realname, email_addr = email.utils.parseaddr(email_string)
    return email_addr


def decode_header_unicode(h):
    """Turns a possibly encoded email header string into a unicode
    string.
    """
    unicodes = [s.decode(enc or 'utf-8') for s, enc in decode_header(h)]
    return u' '.join(unicodes)


def decode_date_header(header):
    """Returns the given email message's Date header as a datetime object.

    The time is of the local timezone.
    """
    uni = decode_header_unicode(header)
    timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(uni))
    return datetime.datetime.fromtimestamp(timestamp)


# By using some not-very-general hackery, we turn
# ENQUIRY_EMAIL_FORMAT into a regexp. To be specific, we
# escape plusses and periods.
ENQUIRY_EMAIL_REGEXP = re.compile(
    settings.ENQUIRY_EMAIL_FORMAT
    .replace('+', r'\+')
    .replace('.', r'\.')
    .format(
        id='(?P<id>\d+)',
        hash='(?P<hash>\d+)'))


def letter_body_template(obj):
    if isinstance(obj, search.models.Representative):
        name = obj.name.split(' ')[-1]
        pref = 'p. '
    else:
        name = obj.name
        pref = ''

    last_name_vocative = multisub_one(
        name,
        (
            (ur'as$', u'ai'),
            (ur'ys$', u'y'),
            (ur'is$', u'i'),
            (ur'us$', u'au'),
            (ur'ė$', u'e'),
        )
    )

    return u"Gerb. {}{},\n\n".format(pref, last_name_vocative)
