"""Slug related utilities.
"""

import re
from django.shortcuts import get_object_or_404
from unidecode import unidecode
from multisub import multisub_all_sequential


SLUG_LEN = 40


def parses_as_int(s):
    """Determines if it possible to parse given string as an integer.
    """
    try:
        x = int(s)
        return True
    except ValueError:
        return False


def strip_dashes(s):
    """Removes dashes from the start and end of string.
    """
    return re.sub(r'^-+|-+$', '', s)


def generate_slug(obj, query, part_getter):
    """Generates slug for 'object'.

    Checks if no other object in 'query' has that slug and tries to
    uniquify it.

    'part_getter' should be a function that takes an object and
    returns a list of possible strings to be used as parts of a slug,
    in order of decreasing importance.
    """
    parts = [multisub_all_sequential(unidecode(p).lower().strip(),
                                     ((r' +', '-'),
                                      (r'[^a-z0-9-]', '')))
             for p in part_getter(obj)]
    parts = [p for p in parts if p != '']
    found = False
    for l in range(1, 1 + len(parts)):
        slug = strip_dashes(u'-'.join(parts[:l])[:SLUG_LEN])
        if (not query.filter(slug=slug).exists() and
            not parses_as_int(slug)):
            found = True
            break
    if not found:
        oldslug = slug
        for i in range(1, 10000):
            s_len = SLUG_LEN - len(u'{}'.format(i)) - 1
            slug = strip_dashes(
                u'{}-{}'.format(oldslug[:s_len], i))
            if (not query.filter(slug=slug).exists() and
                not parses_as_int(slug)):
                found = True
                break
    if not found:
        raise Exception(
            'Unable to create unique slug for {}'.format(
                obj))
    else:
        obj.slug = slug
        obj.save()


def slug_get_or_404(model, id):
    try:
        return get_object_or_404(model, id=int(id))
    except ValueError:
        return get_object_or_404(model, slug=id)
