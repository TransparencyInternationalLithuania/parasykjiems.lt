# -*- coding: utf-8 -*-

import haystack.indexes as indexes
from haystack import site
from unidecode import unidecode

from parasykjiems.web.models import Institution, Representative, Location
import parasykjiems.lang as lang


def join_text(xs):
    """Joins a list of strings using newline as separator and also
    adds transliterated versions of said strings (where they differ
    from the originals).

    Useful for preparing context for indexing.
    """
    return u'\n'.join(set(xs + [unidecode(x) for x in xs]))


class InstitutionIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='name', indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        return join_text([
            obj.name,
            lang.nominative_names(obj.name),
            unidecode(obj.name),
        ])

site.register(Institution, InstitutionIndex)


class RepresentativeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='name', indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        name_variants = lang.name_abbreviations(obj.name)
        kind = obj.kind.name
        return join_text([kind] + name_variants)

site.register(Representative, RepresentativeIndex)


class LocationIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    title = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        return join_text(
            [obj.municipality,
             obj.city,
             lang.nominative_names(obj.city)] +
            lang.street_abbreviations(obj.street)
        )

    def prepare_title(self, obj):
        if obj.street == '':
            return u'{}, {}'.format(obj.city, obj.municipality)
        elif u'miestas' in obj.city:
            return u'{}, {}'.format(obj.street, obj.city)
        else:
            return u'{}, {}, {}'.format(obj.street, obj.city, obj.municipality)

site.register(Location, LocationIndex)
