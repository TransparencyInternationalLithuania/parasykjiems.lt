# -*- coding: utf-8 -*-
"""Language related functions.
"""

import multisub
import itertools


def genitive_to_nominative(word):
    u"""Find possible conversions of a lithuanian word from genitive to
    the nominative case as a set.

    Of course, each word has only one such conversion, but it's
    complicated to determine it, so we just match the words' endings
    and return all possible variants. This is good enough for indexing
    various ways to spell city names for search.

    >>> u'raudonieji' in genitive_to_nominative(u'raudonųjų')
    True
    >>> u'raudonasis' in genitive_to_nominative(u'raudonojo')
    True
    >>> u'Vilnius' in genitive_to_nominative(u'Vilniaus')
    True
    >>> u'Pakonys' in genitive_to_nominative(u'Pakonių')
    True
    >>> u'Gedvydžiai' in genitive_to_nominative(u'Gedvydžių')
    True
    >>> u'Bajorai' in genitive_to_nominative(u'Bajorų')
    True
    """
    c = ur'([bdfghjklmnprsštvwzž])'     # one consonant
    return multisub.multisub_all_separate(word, (
        (c + ur'ųjų$', ur'\1ieji'),
        (c + ur'ojo$', ur'\1asis'),
        (c + ur'osios$', ur'\1oji'),

        (c + ur'iaus$', ur'\1ius'),
        (c + ur'ių$', ur'\1ys'),
        (c + ur'ių$', ur'\1iai'),
        (c + ur'ių$', ur'\1ės'),
        (c + ur'ų$', ur'\1ai'),
        (c + ur'ų$', ur'\1os'),

        (c + ur'io$', ur'\1is'),
        (c + ur'io$', ur'\1ys'),
        (c + ur'o$', ur'\1as'),
        (c + ur'os$', ur'\1a'),

        (c + ur'ės$', ur'\1ė'),
    ))


def nominative_names(thing):
    u"""Turn a genitive title into a list of possible nominative ones.

    Also, removes any lowercase words from the title, to remove
    specifiers like 'miestas' in 'Vilniaus miestas', etc.

    Only suitable for search indexes, not for display, because only
    one of the nominative variants is correct.

    >>> u'Gedvydžiai' in nominative_names(u'Gedvydžių kaimas')
    True
    >>> u'Vilnius' in nominative_names(u'Vilniaus miestas')
    True
    >>> u'Pakonys I' in nominative_names(u'Pakonių I')
    True
    >>> u'Raudonieji Dobilai' in nominative_names(u'Raudonųjų Dobilų')
    True
    """
    words = thing.split(u' ')
    word_variants = [genitive_to_nominative(word) or [word]
                for word in words]
    thing_variants = itertools.product(*word_variants)
    return [' '.join(w for w in variant if not w.islower())
            for variant in thing_variants]


def name_abbreviations(name, abbr_last_name=False):
    u"""Find all possible abbreviations of a multi-word name.

    Ignores any lowercase suffix words. Doesn't abbreviate the last
    name by default.

    >>> streetname = u'Simono Stanevičiaus gatvė'
    >>> r = name_abbreviations(streetname)
    >>> len(r)
    2
    >>> streetname in r
    True
    >>> u'S. Stanevičiaus gatvė' in r
    True
    """
    def abbr(w):
        return w[0] + u'.'

    def sub(namewords):
        if len(namewords) <= 1:
            yield namewords
            if abbr_last_name and namewords:
                yield [abbr(namewords[0])]
        else:
            for variant in sub(namewords[1:]):
                yield [namewords[0]] + variant
                yield [abbr(namewords[0])] + variant

    def istitle(s):
        return s.istitle()

    words = name.split(' ')
    namewords = list(itertools.takewhile(istitle, words))
    endwords = list(itertools.dropwhile(istitle, words))

    result = [u' '.join(name + endwords) for name in sub(namewords)]
    return [x for x in result if x]


def street_abbreviations(street):
    u"""Like name abbreviations, but also abbreviates non-name words
    like 'gatvė' to 'g.', etc.

    >>> r = street_abbreviations(u'Simono Stanevičiaus gatvė')
    >>> u'S. Stanevičiaus g.' in r
    True
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
