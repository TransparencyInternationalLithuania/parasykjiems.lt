# -*- coding: utf-8 -*-

import re

import haystack.indexes as indexes
from haystack import site
from unidecode import unidecode

from web.models import Institution, Representative, Street


def all_abbreviations(name):
    def abbr(w):
        return u'{}.'.format(w[0])

    def sub(namewords):
        if len(namewords) <= 1:
            yield namewords
        else:
            for variant in sub(namewords[1:]):
                yield [namewords[0]] + variant
                yield [abbr(namewords[0])] + variant

    words = name.split(' ')
    return [u' '.join(name) for name in sub(words)]


class InstitutionIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    name = indexes.CharField(model_attr='name', indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        text = u'\n'.join([
            obj.name,
            unidecode(obj.name),
        ])
        return text

site.register(Institution, InstitutionIndex)
