# -*- coding: utf-8 -*-
"""Language related functions.
"""

import parasykjiems.multisub as multisub


def genitive_to_nominative(word):
    """Returns the possible conversions of a lithuanian word from
    genitive to the nominative case as a set.

    Of course, each word has only one such conversion, but it's
    complicated to determine it, so we just match the words' endings
    and return all possible variants. This is good enough for indexing
    various ways to spell city names for search.
    """
    return multisub.multisub_all_separate(word, (
        (ur'ųjų$', u'ieji'),
        (ur'ojo$', u'asis'),
        (ur'osios$', u'oji'),

        (ur'iaus$', u'ius'),
        (ur'ių$', u'iai'),
        (ur'ių$', u'ės'),
        (ur'ų$', u'ai'),
        (ur'ų$', u'os'),

        (ur'io$', u'is'),
        (ur'io$', u'ys'),
        (ur'o$', u'as'),
        (ur'os$', u'a'),

        (ur'ės$', u'ė'),
    ))


def _concat(list_of_lists):
    """Concatenates lists in the list given.
    """
    return [item for sublist in list_of_lists for item in sublist]


def nominative_names(thing):
    """Turns a genitive title into a nominative one. Only suitable for
    search indexes, not for display, because words may repeat if there
    is more than one nominative variant of them."""
    return ' '.join(_concat(list(genitive_to_nominative(word))
                            for word in thing.split(' ')
                            if not word.islower()))


def name_abbreviations(name):
    """Returns all possible abbreviations of person names, as a
    list. Ignores any lowercase suffix words. Doesn't abbreviate the
    last name.

    For example, when passed 'Simono Stanevičiaus gatvė', would return
    the original string and 'S. Stanevičiaus gatvė'.
    """
    def abbr(w):
        return u'{}.'.format(w[0])

    def sub(namewords):
        if len(namewords) <= 1:
            yield namewords
        else:
            for variant in sub(namewords[1:]):
                yield [namewords[0]] + variant
                yield [abbr(namewords[0])] + variant

    namewords = []
    endwords = []
    name_ended = False
    for w in name.split(u' '):
        if name_ended:
            endwords.append(w)
        elif w.istitle():
            namewords.append(w)
        else:
            name_ended = True
            endwords.append(w)

    return [u' '.join(name + endwords) for name in sub(namewords)]


def street_abbreviations(street):
    """Like name abbreviations, but also abbreviates non-name words
    like 'gatvė' to 'g.', etc.
    """
    variants = name_abbreviations(street)
    new_street = multisub.multisub_all_sequential(street, (
        (ur'gatvė', u'g.'),
        (ur'prospektas', u'pr.'),
        (ur'plentas', u'pl.'),
    ))
    if new_street == street:
        return variants
    else:
        return variants + name_abbreviations(new_street)
