# -*- coding: utf-8 -*-

import haystack.indexes as indexes
from haystack import site
from unidecode import unidecode

from web.models import Institution, Representative, Location
import web.lang as lithuanian


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
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_subtitle(self, obj):
        return obj.kind.name

    def prepare_text(self, obj):
        return join_text([
            obj.name,
            lithuanian.nominative_names(obj.name),
            unidecode(obj.name),
        ])

site.register(Institution, InstitutionIndex)


class RepresentativeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)

    title = indexes.CharField(model_attr='name', indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_subtitle(self, obj):
        return u'{}, {}'.format(obj.kind.name, obj.institution.name)

    def prepare_text(self, obj):
        name_variants = lithuanian.name_abbreviations(obj.name)
        return join_text([obj.kind.name,
                          obj.institution.name] +
                         name_variants)

site.register(Representative, RepresentativeIndex)


class LocationIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)

    title = indexes.CharField(indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        return join_text(
            [obj.municipality,
             obj.city,
             lithuanian.nominative_names(obj.city)] +
            lithuanian.street_abbreviations(obj.street)
        )

    def prepare_title(self, obj):
        if obj.street == '':
            return u'{}, {}'.format(obj.city, obj.municipality)
        elif u'miestas' in obj.city:
            return u'{}, {}'.format(obj.street, obj.city)
        else:
            return u'{}, {}, {}'.format(obj.street, obj.city, obj.municipality)

site.register(Location, LocationIndex)
