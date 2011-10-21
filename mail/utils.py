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


MESSAGE_EMAIL_REGEXP = re.compile(
    ur'{prefix}\+(?P<id>\d+)\.(?P<secret>\d+)@{domain}'.format(
        prefix=settings.REPLY_EMAIL_PREFIX.replace('.', r'\.'),
        domain=settings.SITE_DOMAIN.replace('.', r'\.')))


def remove_reply_email(text):
    return MESSAGE_EMAIL_REGEXP.sub("...@" + settings.SITE_DOMAIN, text)


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


def remove_consequentive_empty_lines(string):
    out = []
    was_empty = True
    last_nonempty = 0
    i = 0
    for line in string.split(u'\n'):
        line = line.rstrip()
        if line == u'':
            if not was_empty:
                out.append(line)
                i += 1
                was_empty = True
        else:
            out.append(line)
            i += 1
            last_nonempty = i
            was_empty = False
    print out[:last_nonempty]

    return u'\n'.join(out[:last_nonempty])
