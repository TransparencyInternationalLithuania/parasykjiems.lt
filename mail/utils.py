"""Email-related utility functions.
"""

import re

from email.header import decode_header

import logging
logger = logging.getLogger(__name__)


def extract_name(email_string):
    """Take an email address string and try to extract a name (but not
    the actual address) out of it.
    """

    m = re.match(r'(.+)\s+<.+@.+>', email_string)
    if m:
        return m.group(1)

    m = re.match(r'.+@.+\s+\((.+)\)', email_string)
    if m:
        return m.group(1)

    m = re.match(r'(.+)@.+', email_string)
    if m:
        return m.group(1)

    logger.warning("Can't extract name from email '{}'.".format(email_string))
    return ''


def decode_header_unicode(h):
    """Turns a possibly encoded email header string into a unicode
    string.
    """
    unicodes = [s.decode(enc or 'ascii') for s, enc in decode_header(h)]
    return u' '.join(unicodes)
