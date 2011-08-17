import re
from unidecode import unidecode

_REMOVE_PUNCTUATION_RE = re.compile(ur'[^\w/ ]', flags=re.UNICODE)
_NORMALISE_SPACES_RE = re.compile(ur'(\s)\s+')

_FIND_HOUSE_NUMBER_RE = re.compile(
    ur'''
    (.*\s|)
    ( \d+\w? ) (?: / \d+\w? )?
    (\s.*|)
    $
    ''',
    flags=re.UNICODE | re.VERBOSE)


def remove_house_number(q):
    """Removes house number from search query string.

    Returns duple of new search query string and extracted house
    number (as a string). If the string doesn't contain a house
    number, returns '' instead.
    """
    q = _REMOVE_PUNCTUATION_RE.sub(u' ', q)

    m = _FIND_HOUSE_NUMBER_RE.match(q)
    if m:
        pre, num, post = m.group(1, 2, 3)
        q = pre + post
    else:
        num = u''

    q = _NORMALISE_SPACES_RE.sub(u' ', q)

    return q.strip(), num


_REMOVE_DASHES_RE = re.compile(ur'-')


def normalize_auto(term):
    """Normalises search term for autocompletion search."""
    return _REMOVE_DASHES_RE.sub(u'', unidecode(term))
